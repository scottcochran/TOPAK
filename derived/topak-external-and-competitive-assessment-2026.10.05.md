# TOPAK External and Competitive Assessment

**2026.10.05** · derived · assessment, not a record · **design level only** for the competitive half: what each design
commits to and how it is structured, not whether it works, how fast, how mature, or whether anyone has adopted it ·
TOPAK basis: Genesis Checkpoint G10 (2026.10.05) and Theory of Operation revision 14, at `f462953` · regenerates and
combines `topak-competitive-design-assessment-2026.10.01.md` (against G7 and revision 11) and
`topak-external-assessment-2026.09.12.md` (against the 09.12 checkpoint; marked historical), which it supersedes as
basis · external references: Moon & Varshney arXiv:2605.09045v2, read this time from the arXiv HTML and the PDF at
`doc/2605.09045v2.pdf`; the NIST AI RMF 1.0 Playbook, unchanged; the TACIP community-of-interest discussion draft of
**2026.09.28(a)** at `doc/DiscussionDraft_NIST_AIRMF_TACIP_20260928a.md`, one draft later than the one the 10.02
review graded; and the comparables of §3, each re-read from primary text where §12 says so · prepared by Claude in
one session at the custodian's request

Nothing here is ratified, and this document proposes no decision text. Where it says a gap is closed it means the
design now says something, in a record in force; "in force" at G10 includes records that are confirmation-required and
two that are provisional, and those are marked. Part I is the field; Part II is the two external references and the
standards that have grown up around them since September; Part III is what to do about it.

---

## 0. Verdict

**The field has started to compute what a policy change adds. Nobody but TOPAK governs who may approve it.** That is
the one-sentence change since the 10.01 assessment. On 10.01, computed classification of a policy change was
TOPAK's alone with one unverified rumour beside it. On 10.05 the rumour is confirmed as the third version of the
Progent paper, which checks with Z3 that a revised privilege policy only narrows, auto-applies narrowings and routes
expansions to an approver (§3.7); OpenShell binds every pending widening to a review token and re-evaluates it at every
policy change (§3.2); a two-tier Cedar design from a second team proves on paper that its lower tier can only
restrict and names change control as its own open limitation (OBPE, §3.9); and an "execution-boundary conformance
profile" requires that an operational policy never weaken a root policy and that a grant be re-checked at redemption
against the policy versions it was adjudicated under (EBL-Core, §3.9). Each of these is a convergence toward one
piece of TOPAK's Build-side structure. None treats the approver as an object to be governed. In every one the
regress still ends in an operator, a console, a configuration flag that may say `auto-approve`.

**Of the three design-level gaps the 10.01 assessment named, two are closed in records in force and the third is a
stated position.**

1. **Provenance on arguments (A14).** ADR-0047 labels every item of Run ingress by its declared source, delivers
   suppressed items as handles whose bytes never enter the guest, keeps a round-scoped monotone bound (`clearSet`),
   and puts three forbids in the floor that a bundle cannot loosen. It is a coarser instrument than CaMeL's or FIDES's
   per-value tracking, by design: a label is a syntactic lift from a declaration, not a finding about content. The
   module that checks it found and closed a laundering hole the record had missed.
2. **Tool descriptions (A14's neighbour).** ADR-0048 and ADR-0049 did not pin the interface text by digest, as the
   10.01 assessment suggested. They did something stronger for the threat and weaker for the audit: the interface is
   part of the allowlist entry, so it passes promotion like any bundle change, and the mechanism delivers it to the
   Thinker as the round's opening record; a Persona's or a task's description of a tool has no standing. The entry's
   digest covers artifact and input types only; the interface rides on the bundle revision and its signature.
3. **History-dependent policy (A15).** Decided for the archetype: no temporal operator enters the policy language.
   History reaches policy as a fixed set of folds the mechanism computes (`clearSet`, sequence number, round count),
   each added by mechanism release. Dogwood's MFOTL layer is the road not taken, and the record says why.

**Two gaps the 10.01 assessment did not weigh are now the ones the field makes visible.** First, **delegation**: a TOPAK
principal cannot create a subordinate, so there is no chain to attenuate, no cascade to model and no record stating
that as a position, while the identity standards (WIMSE AIMS, ID-JAG, attenuating tokens), the vendor control planes
(Entra Agent ID, Vault ceilings) and a run of September papers all build around chains. Second, **the refinement to
code (A19)**, still the one artifact Moon & Varshney have and TOPAK does not; stage one is current and found a race,
stages two and three are not begun.

**Against the externals.** Moon & Varshney, re-read from the text: no v3, two citing papers, a workshop poster, no
follow-up from either author; every section pointer in the corpus checks except one ("failure taxonomy" is the end of
§3.5, *Mechanization*, and has no name), and one live miscitation remains in ADR-0024 after ToO §7.1 was fixed. The
Playbook is unchanged and no AI RMF 1.1 draft exists; the 10.03 inventory stands, and this document records what G10
would move. TACIP's 09.28(a) draft is minor and four of its changes land on TOPAK by name: a refused action
part-way through a sequence, the watchdog as attack surface, self-attestation as insufficient for *Verifiable*, and the
inference receipt recording the rules applied. The frameworks that have appeared around agents since September
(OWASP's agentic top ten, NIST's agent-identity concept paper, the Five Eyes guidance) ask for immutable signed logs,
governed identity and change control over goals and permissions. OWASP ASI08 names "policy relaxations" propagating as
"governance drift" as a failure mode, which is TOPAK's premise stated by a standards body. The Five Eyes guidance,
read from the PDF, asks for separation of duties by roles like "Reader" and "Actuator" with "consensus mechanisms,"
forbids agents "modifying their own privileges or initiating unapproved delegation without explicit expiry timers and
recorded grant chains," and wants tool descriptions that avoid "persuasive language" and log-deletion requests
quarantined for a human: five of TOPAK's records, recommended by six governments. None of them asks who may approve
the relaxation.

**One-line positioning, unchanged.** The rest of the field governs *what the agent may do*. TOPAK governs that, and in
addition *who may change what the agent may do, how that change is classified, and what record survives it*. The
competitor is still the assumption every comparable shares: that the policy author is trusted. In October it is a
little less safe to say the field has not noticed the assumption; it has begun to check the author's work. It has not
begun to doubt the checker.

---

## 1. Scope, method, and what was reachable

**Design level**, as on 10.01: components and their trust relations; where enforcement happens; the policy language
and how policies compose; who may widen authority; what is ordered and recorded; what is verified, and about which
object. It excludes performance, correctness of implementation, adoption, maturity and release status. A design that
is announced and unbuilt is assessed as designed and marked. The axes (§2) are TOPAK's own, because the question is
where TOPAK stands; §6 corrects for that.

**What is new in method.** The 10.01 assessment read most comparables through search summaries and said so. This one
read the Moon & Varshney text (arXiv HTML v2, and the PDF the custodian supplied), the OpenShell repository through its
API, the AgentCore and Dogwood documentation and repository, the FIDES and Agent Governance Toolkit documentation and
changelog, the Progent v3 text, the Temporal documentation, the `sandbox-runtime` repository and the Claude Code
sandboxing documentation, the MCP authorization specification and its extensions repository, the IETF datatracker,
and the new papers of §3.9 at abstract or full-text level. What was still read through summaries is in §12.

**Reachable this session**: arxiv.org, nist.gov, csrc.nist.gov, github.com, learn.microsoft.com, docs.aws.amazon.com,
docs.temporal.io, modelcontextprotocol.io, datatracker.ietf.org. **Not reachable or not public**: OpenReview (bot
challenge); any TACIP draft newer than 09.28(a) (community-of-interest only); Sentry's internals (none published);
Google Scholar. The Five Eyes "Careful adoption of agentic AI services" PDF returned 403 from two hosts and was
supplied by the custodian at `doc/careful_adoption_of_agentic_ai_services.pdf` during the session; §8.5 reads it.

**The TOPAK side** was read from the records, the ToO, G10 and the 10.03 derived documents, with a status audit of
every open item the two source assessments raised (§7.3, §10). Three of the 10.03 documents predate G10 and say floor
fitness is unowned, R8 is pending and ADR-0005 is Proposed; G10 supersedes them on all three, and this document reads
G10.

---

# Part I — The field

## 2. Design matrix

Legend: **●** the design commits to it as a structural property · **◐** partially, optionally, or as a manual or
out-of-path check · **○** absent · **—** out of the design's scope by intent · **Δ** the TOPAK cell changed since 10.01.

| Axis | TOPAK | Moon & Varshney | OpenShell (+Sentry) | Temporal | AgentCore + Dogwood | CaMeL / CaMeLoT | FIDES | MS AGT | Progent v3 | OBPE | EBL-Core |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A1** Model out of the trusted base | ● | ● | ◐ ¹ | — | ● | ◐ ² | ◐ ² | ○ ³ | ● | ● | ● |
| **A2** Closed, typed action alphabet | ● | ● | ◐ ⁴ | ○ | ◐ ⁵ | ● ⁶ | ○ | ○ | ◐ | ◐ ²² | ◐ ²³ |
| **A3** Semantic judgment can only subtract | ● | ● | ○ | — | ◐ ⁷ | ● | ● | ○ | ◐ ²⁴ | ● | ● |
| **A4** Policy tier with mechanized semantics | ● Cedar floor | ● Dafny | ◐ Rego + Z3 model | ○ | ● Cedar | ◐ ⁸ | ○ | ◐ ⁹ | ◐ ²⁵ | ◐ ²⁶ | ◐ ²⁷ |
| **A5** Composition is monotone (later layers only narrow) | ● | — ¹⁰ | ○ ¹¹ | — | ◐ ¹² | ● | ● ²⁸ | ○ | ◐ ²⁹ | ● ³⁰ | ● ³¹ |
| **A6** Policy *change* governed and classified | ● | ○ | ◐ ¹³ | ○ | ○ ³² | ○ | ○ | ◐ ³³ | ● ³⁴ | ○ ³⁵ | ◐ ³⁶ |
| **A7** Authority over the rule-makers (anchor, rules floor) | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A8** Separation of duties among agents | ● seats, cells, recusal, operators | ○ | ○ | ○ | ○ | ◐ ¹⁴ | ◐ ¹⁴ | ◐ ¹⁵ | ○ | ○ | ○ |
| **A9** Total order over authority-changing decisions | ● Paxos | ○ | ○ | ◐ ¹⁶ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ ³⁷ |
| **A10** Denials in the record | ● | ○ | ● | ○ ¹⁷ | ● | ◐ | ◐ | ● ³⁸ | ○ | ● | ◐ ³⁹ |
| **A11** Erasure and legibility modeled | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A12** OS / guest confinement | ● designed, rung 1 built | ◐ assumed | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A13** Attested confinement | ● rung 3 designed, SIMULATED | ○ | ◐ Sentry, of the watcher | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A14** Provenance / data flow on arguments | **● Δ** ¹⁸ | ○ | ○ | ○ | ○ | ● | ● | ○ | ○ | ◐ ⁴⁰ | ○ |
| **A15** History-dependent policy | **◐ Δ** ¹⁹ | ◐ loop bound | ○ | — | ● MFOTL | ● CTL over plan | ○ | ◐ trust score | ○ | ◐ design only | ○ |
| **A16** Detection placed by rule, deny-only, cross-family | ● designed, unbuilt | ○ | ◐ Sentry placement | ○ | ○ | — | — | ○ | ○ | ○ | ○ |
| **A17** Model identity pinned | ● Persona | ○ | ○ | ○ | ○ | ○ | ○ | ◐ DID per agent | ○ | ○ | ○ |
| **A18** Verification object is the mechanism | ● TLAPS + op. model | ● | ○ ²⁰ | ○ | ○ | ◐ the plan | ○ | ○ | ◐ the comparison | ◐ paper proofs | ○ |
| **A19** Refinement to running code | ○ T-0045-28, stage 1 only | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A20** Durable, replayable execution | ◐ ²¹ | ○ | ○ | ● | ○ | ○ | ○ | ◐ sagas | ○ | ◐ design only | ○ |
| **A21** Trusted base declared row by row | ● 36 rows | ● short list | ◐ prose | ○ | ○ | ◐ | ◐ | ○ | ○ | ◐ | ○ |
| **A22** Delegation chains modeled or refused in a record | **○** ⁴¹ | — | ◐ parent/child prover | ○ | ○ | ○ | ○ | ◐ inter-agent trust | ○ | ○ | ○ |

1. OpenShell's enforcement is model-free; its supervisor middleware, Guardrails and Nemotron classifiers can *allow* or
   *rewrite*, optionally and outside the core.
2. CaMeL and FIDES keep the *quarantined* model out of authority; the *planner* model is trusted to write the plan.
3. AGT's trust score, 0–1000, sets privilege rings and can include a semantic intent classifier, so a model's
   judgment can *raise* privilege.
4. OpenShell's MCP tool-call allow-lists and per-binary L7 rules type the wire. The agent still has a shell.
5. AgentCore types the gateway's tool calls. The agent may hold other channels.
6. CaMeL's restricted Python plan is a closed language. Its tools are not.
7. AgentCore authors Cedar from natural language, with automated reasoning on the result (always-allow, always-deny,
   unsatisfiable). Confirmed from the documentation this time.
8. CaMeL's policies are Python predicates. CaMeLoT model-checks the plan, not the policy.
9. AGT accepts Cedar or Rego; since v5 its native layer is the Agent Control Specification, a Rust-backed deterministic
   runtime compiling to Rego, with a classifier beside it.
10. Moon & Varshney verify one fixed policy and have no change cadence.
11. OpenShell merges rules permissively; a global policy replaces sandbox policy.
12. Cedar's forbid-overrides is monotone within one policy set; Dogwood's temporal conditions add to it. Nothing bounds
    a revision.
13. OpenShell's prover computes the reach a proposal adds; since #3923 (10.01) every pending proposal is re-evaluated at
    every policy change and bound to a review token, and approval rejects a stale token. A manual, out-of-path check with
    no authority routing; a CAS on policy revisions is a draft PR (#4219).
14. The privileged/quarantined split is a duty separation *inside one agent*.
15. AGT's privilege rings are separations by score, not by role.
16. Temporal fences shard ownership with a RangeID over a database transaction: an order within a workflow, not over
    decisions about authority. Principal Attribution (pre-release) stamps *accepted* history events with a
    server-derived principal.
17. Confirmed from the documentation: an Update a validator rejects leaves "no indication that it was ever requested"
    in the Workflow's history.
18. **Δ.** ADR-0047 (in force, confirmation-required). A label is a set of names from a bundle-declared vocabulary with
    two reserved by the floor (`untrusted`, `restricted`); it is a function of the item's declared source (grant, Run
    root, allowlist entry, bundle); items are delivered clear with their label or as handles with no bytes; `clearSet`
    is the join of everything delivered clear this round and only grows; three floor forbids (`R5`–`R7`) are monotone in
    it. Per-item and per-round, not per-value: flow through the model is bounded, not traced. Build's `Read` is not
    labelled. See §3.5.
19. **Δ.** History reaches policy only as a fixed set of mechanism-computed attributes (`clearSet`, sequence number,
    round count), each added by mechanism release; no temporal operator in the policy language (ADR-0047 R13, ADR-0030
    A2). A position now, not a gap. `K` is a floor value; `R` a mechanism parameter.
20. OpenShell's prover verifies a *policy's* reach, not the supervisor.
21. TOPAK's log can replay what crossed the membrane. It does not resume a crashed computation, by design.
22. OBPE's boundary is the tool API, typed by its own annotations (`@transform`, `@field_group`, `@cap_limit`) on
    Cedar.
23. EBL-Core's actions are structured intents adjudicated into grants; the agent's other channels are out of scope.
24. Progent's task policy is LLM-generated and LLM-revised; the revision is admitted only if Z3 shows it narrows. The
    semantic step authors; the mechanical step gates.
25. Progent's conditions are JSON-Schema predicates compared by Z3; the DSL has no mechanized semantics of its own.
26. OBPE uses Cedar's analyzer for the permit/forbid subset only; its annotations sit outside the verified language,
    and its three propositions are paper proofs.
27. EBL-Core states its properties formally and "disclaims mechanized correctness."
28. FIDES: labels combine by the most restrictive per axis; MCP-supplied labels "can only restrict, never relax" unless
    the server is explicitly trusted. The same rule as ADR-0047's "a bundle cannot loosen the floor's minimum."
29. Progent: fixed generic policy over task policy, forbid wins; a task policy can still allow what the generic tier
    did not forbid.
30. OBPE Proposition 3 (Tier Refinement): the agent policy can only restrict the owner policy; Proposition 2:
    adding a stage restriction cannot enlarge the plan.
31. EBL-Core: "Operational policy cannot remove, weaken, rename, or reinterpret an obligation" of the root policy;
    Allow(K,P) ⊆ Allow(K,∅).
32. AgentCore: adding or updating a temporal policy invalidates active sessions (HTTP 409); no version identifiers,
    approval or classification found in the pages read (§12). The permission that flips `ENFORCE` to `LOG_ONLY` is the
    same `UpdateGateway` permission.
33. AGT: audit entries now carry a `policyVersion` tying each decision to the policy that produced it, and hash-chain.
    Versioned, not governed.
34. Progent v3 §4.3 and §6: P′ narrows P iff ∀v̄. Φ_{P′}(v̄) ⇒ Φ_P(v̄) per tool, checked by Z3; narrowings
    auto-applied; expansions "requiring explicit approval" under an approver configuration that may be auto-deny,
    auto-approve, manual or per-tool. "Monotonic confinement": A(P⁽⁰⁾) ⊇ A(P⁽¹⁾) ⊇ … without approval. Classified and
    routed; the approver is a configuration.
35. OBPE lists change control as a limitation: "named owners, coordinated policy-and-schema rollout, rollback, and
    review," with no mechanism.
36. EBL-Core content-addresses policy versions ("any semantic change requires a new identifier") and re-checks all
    versions at redemption; changes to the root policy are not governed.
37. EBL-Core requires grant-lifecycle transitions (ISSUED → CONSUMED / EXPIRED / REVOKED) to be linearized, and
    re-checks policy versions, obligations and the time window at redemption. A linearization requirement with no total
    log; the artifact is an in-memory store.
38. AGT's hash-chained logs record decisions with `reason`, `argsDigest` and a declared, unverified `principal`.
39. EBL-Core produces a structured denial derivation with a priority-ordered reason code; it "need not be stored."
40. OBPE narrows queries and filters response data before the agent sees them: data minimization at the boundary, not
    provenance on what the agent later sends.
41. TOPAK: a principal cannot create a subordinate (ADR-0037's one-seat rule); there is no chain and no record that
    states the absence as a position. Design-gap assessment row 1.3; four reviews have asked.

**Reading the matrix.** Down the TOPAK column, A14 moved from the only hole to a ● with a footnote, and A22 is the new
hole. Across rows A7 and A11, TOPAK is still alone. Across A9 it is alone in kind, and EBL-Core's linearized grant
lifecycle with re-check at redemption is the first design to ask for the second half of what the row means. Across A6
it is no longer alone in kind: Progent v3 classifies and routes; what it routes to is whatever the deployment
configured. Across A5, the monotone-composition rule that TOPAK stated for policy in ADR-0010 is now stated by five
designs for five objects (Cedar tiers, labels, MCP annotations, root policies, privilege sets), which is what a
design pattern looks like when it has stopped being one project's.

---

## 3. The comparables, one at a time

### 3.1 Moon & Varshney

Design-level content is in Part II (§7). Two design facts for this half: the paper is unchanged since 2026.06.29 and
has no successor, and nothing published in 2026 does what it does, a deductive, machine-checked refinement from
abstract boundary specification to running code of an agent framework. The nearest 2026 work verifies something else:
Lean4Agent models agent workflows and trajectories in Lean 4; Hu, Goel and Bindschaedler check the *effects* of
LLM-regenerated systems code through a fixed mediator at runtime (and cite the paper); Metere's capability-containment
proof uses abstract interpretation and SMT with no proof assistant. TOPAK's position relative to the paper is the one
ToO §11.1 states: the modules' invariants are proved (22 modules, 5,225 obligations, 19 certified), and the running
reference is still *Empirical* in the paper's ordering S(Empirical) ⊆ S(Distributional) ⊆ S(Universal), stated in
§2 beside Table 1.

### 3.2 NVIDIA OpenShell: what changed since 2026.10.01

The 09.28 comparison and the 10.01 delta stand. Since `348a1fc`, read from the repository through its API:

- **Pending widenings are bound to their evaluation** (#3923, 10.01). The gateway re-evaluates every pending policy
  proposal at every policy change and binds it to a review token over its inputs; approval of a stale token is
  rejected. This is the shape of ADR-0030 §5's "a decision counts only from a named revision", done for proposals
  rather than for the floor, and still out of path.
- **A policy revision is becoming a version** (#4219, draft, 10.05): compare-and-set on policy revisions, so a writer
  holding a stale version gets a conflict rather than overwriting an intervening change. Ordering of policy changes,
  per sandbox, by optimistic concurrency.
- **Fail-closed startup** (#3785): a workload whose startup policy write the gateway refuses stays stopped until the
  policy is repaired.
- **A merge-time "who may widen" check** (#4171, open, re-filed from an external PR the vouch bot bounced): enabling
  `allow_uninspected_credentials` on a shared endpoint now has to name every binary, closing a path where a binary
  joining a rule silently inherited the exemption. The gap it closes is a composition hole of exactly the kind the
  10.01 assessment's footnote 11 described.
- **Identity**: sandbox identity separated from TLS (#3110, merged minutes before the 10.01 read), bearer-token bootstrap
  and sandbox JWTs at the gRPC boundary; a draft (#4217) to stop only the *attested execution*, rotating launch identity
  on recovery so old credentials cannot bootstrap a replacement. Direction: toward the lease as an identity bound to
  one execution, which is ADR-0031's.
- **Recording hygiene** (#4005): agent output no longer lands in gateway status and events, "including anything
  sensitive." The control-plane/payload separation of ADR-0004, arrived at from the other side.
- **Sentry**: nothing new. The 09.28 blog remains the only primary text; deny-only, failure direction, what is
  attested and the record format are still unstated. Every "fail-closed" and "attested telemetry" claim in circulation
  is secondary.
- **No new RFCs**; RFC 0011 (multi-player) unchanged since 09.11; no release since v0.1.2 (09.28). The policy language,
  MCP inspection and OCSF audit did not change in the window.

Direction of travel since 09.28: toward TOPAK's structure on A6 (review tokens, CAS), A10 (attributed denials), A17
(execution-bound identity) and the control/payload split; away from it on none. The regress still ends at the console.

### 3.3 Temporal, Restate, DBOS

The 10.01 table of design differences stands, with three confirmations and one addition:

- **Rejected Updates leave no history**, confirmed from `docs.temporal.io/handling-messages`: "the Workflow will have
  no indication that it was ever requested." ADR-0020's recorded denials have no counterpart, and Principal
  Attribution, which stamps accepted events with a server-derived principal, has nothing to stamp on a refusal.
- **The Agent Harness has grown a tool-approval policy** (0.6.0, 10.03): static allow-list, by-name pre-approval, and an
  "auto mode" in which a swappable evaluator judges *arguments* against operator-owned criteria, with the gate
  escalating to a human on low confidence, an irreversible effect, a raise, or an evaluator outage ("It can't fail
  open"). Handlers that move the guardrail are marked not model-callable. This is a semantic step in the admit path
  (ADR-0007 would refuse it as an admit; it would accept it as a detection that can only send a call to a human), and
  the "cannot fail open" rule is the right failure direction. The evaluations are bracketed on the event stream.
- **Replay 2026 was 2026.05.06**; Worker Versioning GA, Nexus GA for Python. Nothing on authorization since.
- **Restate** states the versioning hazard TOPAK closes by construction: without pinning, "a human approval granted
  under one policy gets treated as an approval under a different one." Its answer is pinned deployments; TOPAK's is the
  lease's bundle revision and a round that ends when the rules change. **DBOS** has declarative role checks and
  Conductor audit logs; no per-tool policy. Neither has a change-control design.

### 3.4 AWS Bedrock AgentCore Policy, and Dogwood

Read from the documentation and the repository this time. The 10.01 characterization holds, with corrections and
three design facts that matter:

- **Dogwood is a reference interpreter** ("not for production use"), Apache-2.0, last pushed 2026.09.17, no release. Its
  operators (`formerly within`, `since within`, `previous`, `count`, `sum`, …) are standard-library macros over a core
  MFOTL subset. In AgentCore the *service* owns the history; in the open-source form the caller feeds events.
- **The history is scoped to a caller-supplied session ID.** With a temporal policy present, a request without the
  header fails; a rate limit therefore "constrains activity within a session rather than across all of a caller's
  sessions," which the documentation says. TOPAK's corresponding scope is the round topic, which the mechanism names
  and the principal cannot choose.
- **A policy change invalidates sessions**, and that is the whole change model: no version identifiers, no approval,
  no classification, and the Cedar analysis "does not currently support" temporal conditions. The permission that
  flips `ENFORCE` to `LOG_ONLY`, or removes the engine, is the gateway's ordinary update permission.
- **Guardrails as information providers**: a content-safety or prompt-attack *score* can now be a Cedar attribute. A
  semantic signal in the admit path, where ADR-0007 allows it only as a detection.

Design relationship unchanged: the nearest policy-tier design, made the same language choice for the same reason,
and composes one policy set edited by whoever holds the console. The A15 contrast is now a contrast between two
positions rather than a gap: Dogwood puts a temporal logic in the policy; TOPAK puts a fixed set of folds in the
mechanism and lets policy read them as attributes.

### 3.5 CaMeL, CaMeLoT, FIDES — and ADR-0047

CaMeLoT is confirmed: arXiv:2609.18674, accepted at CAMLIS 2026, from Oslo and Edinburgh rather than DeepMind;
plans become finite-state systems labelled with tool calls, provenance and taint, checked against CTL with nuXmv. FIDES
is documented in the Agent Framework as of today (updated 2026.10.05): a two-axis lattice (integrity
{trusted, untrusted}; confidentiality {public < private < user_identity}), unlabelled tool output defaulting to
untrusted-public, `var_<id>` handles for hidden untrusted results, a quarantined tool-free model to process them, a
deterministic check against sink annotations before a consequential call, and, new, **MCP-supplied labels that can
only restrict**.

**What TOPAK built, against these.** ADR-0047 is in force. The comparison is now between three designs for the same
goal, and the differences are instructive:

| Concern | CaMeL / CaMeLoT | FIDES | TOPAK (ADR-0047) |
|---|---|---|---|
| Unit labelled | Every value in the interpreter | Every message and variable | Every *item of ingress* (task, `Consult` content, `Actuate` result, tool list) |
| Where the label comes from | Computed by the interpreter from the plan's dataflow | Propagated by the framework; defaults fail closed | **Declared** by the item's source: the grant, the Run root, the allowlist entry, the bundle. A syntactic lift, "not a judgment about content" |
| How untrusted content is kept from the planner | A second, quarantined model parses it | A handle (`var_id`) and a quarantined model | A **handle** with no bytes, delivered by the Listener; the tool host resolves it; no second model |
| Flow through the model | Tracked per value by the interpreter | Hidden; revealed by explicit operation with audit | **Bounded, not tracked**: `clearSet`, the join of every label delivered clear this round, only grows; a literal argument inherits it (R10) |
| The floor's minimum | Policy author's | Sink annotations | Three forbids on an *outward* `Actuate`: read-then-send, steered destination, replayed destination; a bundle may deliver everything clear and cannot escape them |
| Who sees everything | — | Audit log | The Observer: the `Actuate` record carries inputs, result, labels, delivery mode and `clearSet` |
| What it does not cover | Planner is trusted | Developer labels are trusted | A wrong declaration; flow item by item; injection through `Report` or a non-outward entry; Build's `Read` |

TOPAK's instrument is coarser and its trust base is smaller: nothing inside the mechanism parses content, and the
labels are computed from declarations the record already holds. The cost is stated in the record and in ToO §12 item
18: a source declared trusted that is not "is seen by nothing," and the task's label is the operator's word. The
module found a hole the drafting missed, a literal laundered through an inside tool, and R10 closes it; that is the
formal layer doing what it is for. CaMeL's and FIDES's per-value tracking remains the stronger instrument *inside* the
envelope, at the price of a trusted interpreter or a trusted framework in the fault domain of the agent.

### 3.6 Microsoft Agent Governance Toolkit, Entra Agent ID

AGT since 10.01: packages consolidated, the Agent Control Specification (v5) is the native policy layer, hash-chained
audit entries carry `reason`, `argsDigest`, a *declared* principal and a **`policyVersion`**, and a run of fail-closed
fixes to the Rego compiler and to scope validation (a misspelled scope previously became `GLOBAL` and could flip a
deny to an allow). Enforcement remains in-process, through SDK adapters and editor hooks. The trust score still moves
upward. The design relationship is as stated on 10.01: the plainest opposite of TOPAK on A3, and a convergence on
A10 and now on policy versioning, which TOPAK carries in the lease.

**Entra Agent ID and Agent 365** are an identity and entitlement design, not a policy one: agent identities as a third
account class, created from blueprints that pass permissions and Conditional Access down, each with a human sponsor;
authority either autonomous (roles granted to the identity) or delegated (on behalf of a user, who controls what is
delegated); access packages with request, approve, review and expire. It governs *who the agent is and what it is
entitled to*, with approval at entitlement time. No per-call policy language, no narrowing check, no change
classification. It is the clearest statement of the industry's answer to A22, and TOPAK has none.

### 3.7 Progent v3, AgentSpec, Invariant/Snyk

- **Progent.** The "monotonic confinement" extension the 10.01 assessment could not attribute is **v3 of
  arXiv:2504.11703** (2026.05.14), retitled "Securing AI Agents with Privilege Control." The DSL is as described
  (per-tool rules, forbid before allow, default deny, a fixed generic policy evaluated first). New in v3 is §4.3,
  policy comparison by SMT: a proposed task policy P′ is a narrowing of P iff, per tool, every argument P′ allows P
  allowed, checked with Z3; narrowings are applied without approval, expansions require it, and the approver is
  configured (auto-deny, auto-approve, manual, per-tool). §6 states the guarantee: the agent's action space cannot
  increase without explicit approval.

  **Design relationship.** This is ADR-0030 §5's computed classification, one tier down and three steps short.
  Shared: a mechanical, decidable test for "does this change only subtract," applied before the change takes effect,
  with the cheap path open only to subtraction. Absent: the approver is a configuration value, not a principal with a
  seat, a recusal rule and a roster bounded by a floor; the generic tier is trusted and has no change model; nothing
  is ordered or recorded; and the policy author is an LLM the design *trusts to propose* and *checks*, which is
  exactly the right amount of trust for Run and says nothing about Build. It is the first comparable to make the
  10.01 assessment's §4 item 3 untrue as written, and §4 below rewrites it.
- **AgentSpec** is as described (trigger/check/enforce; `llm_self_examine` repairs the action; LangChain hooks); no
  2026 follow-up from its authors.
- **Invariant / Snyk.** The design has moved under the product. `invariant` (Guardrails) was last pushed 2026.01.12.
  `mcp-scan` is now `agent-scan` ("Snyk Agent Scan", v0.6.8, 2026.09.29); its current CLI documents `scan`, `inspect`,
  `evo`, `guard`, and no `proxy`, no guardrail rules and no tool-description hashing. The rug-pull detection the 10.01
  assessment cited exists in the project's history and is not in the current product's documentation (source not
  inspected, §12). The analysis runs server-side at Snyk. For the design question, pinning the interface a Thinker
  reads, the field's answer has moved to the protocol, and the protocol declined it: MCP SEP-1766 (digest-pinned tool
  versioning) was closed 2026.06.25 and SEP-3140 (signed capability declarations) closed unmerged 2026.09.22; still open
  are SEPs on trust annotations, tool risk metadata, attested tool-server admission and structured denials. TOPAK's
  ADR-0048/0049 answer, the interface as part of a promoted bundle delivered by the mechanism, is the only design in
  this survey where a tool's description has to pass the same gate as a policy change.

### 3.8 Anthropic `sandbox-runtime` and Claude Code sandboxing

Since 09.01 (v0.0.75 → v0.0.78): a resolved-address guard (a permitted hostname that resolves to a denied address is
refused, and the proxy dials the vetted address itself); **violation attribution** under a per-command key, with a
model-facing reason for a network deny; experimental TLS termination; mandatory-deny hardening against rename and
mid-wrap binds; credential masks that win over carve-outs. In Claude Code, an **admin-required sandbox**: when managed
settings forbid unsandboxed commands, project and local settings "cannot widen or turn off" the sandbox, replace the
proxy behind a managed deny list, extend a strict allowlist or reopen managed read-denies; `deny` credential entries
merge from every scope and "no scope can remove one that another scope added"; masking (which authorizes the proxy to
send a real credential somewhere) is honoured only from user, managed or `--settings` scope. Protected paths are
write-denied because a command that could edit them "could grant itself permissions."

**Design relationship.** Still a rung-1 launcher failing P3, P4 and P5, now with three things worth naming. The
scope rule is a monotone composition rule for *configuration*: lower scopes may only narrow, and the operations that
can add reach (masking, TLS termination) are accepted only from the scopes that own the risk. That is ADR-0030's
floor/bundle direction applied to settings files, and it is the first time a shipped developer tool has stated it as a
rule. The protected-paths rule is the trusting-trust concern of ToO §11.1 item 5 in one sentence. And the
documentation's limitations section says what it does not do (client-supplied hostname, no TLS inspection by default,
domain fronting), which is the register TOPAK uses. No prover, no attestation, no record beyond the violation log.

### 3.9 New in this survey

The landscape scan (§12 for method) returned about seventy items. Most are proposals with one evaluation; the table in
§8.5 of the standards half names the ones that matter for frameworks. Eight touch TOPAK's Build-side commitments and
are read here at design level.

- **OBPE, "If Agents Were Angels, No Governance Would Be Necessary"** (Millstone, Akidau, Brüderl, Pekker;
  arXiv:2608.27646, 2026.08.27; full text read). Two Cedar tiers at a trusted tool boundary: an *owner* policy, the
  only tier that can create permit eligibility, and a registered *agent* policy that can only restrict (Proposition 3,
  Tier Refinement); default deny; every decision an audit record; queries narrowed and responses filtered before the
  agent sees them. The closest design in the survey to ADR-0010's floor/bundle split, arrived at from data stewardship.
  It differs in three ways the paper itself names: its proofs are on paper and its annotations sit outside Cedar's
  verified subset; durable approval and temporal policy are "design only"; and policy-change governance is a stated
  limitation, "named owners, coordinated policy-and-schema rollout, rollback, and review," with no mechanism. It is the
  field's clearest acknowledgment that the layer above the two tiers is missing.
- **EBL-Core, "From Intent to Execution Grant"** (Wu, Wang, Zhang, Deng; arXiv:2609.11596, 2026.09.10; full text
  read). A root policy K and an operational policy P with *root-policy dominance*: P cannot remove, weaken, rename or
  reinterpret an obligation of K. Grants have a lifecycle (ISSUED → CONSUMED, EXPIRED, REVOKED) whose competing
  transitions must be linearized, and **redemption re-checks** that every policy version equals the one adjudicated
  under, every obligation is still valid and the time is in window. Denials produce a derivation with an ordered reason
  code. This is the first comparable to ask for the second half of A9, an apply-time re-check against the version the
  decision was made under, which TOPAK does with the fence as log index and the bundle revision in the lease. EBL-Core
  mandates linearization and no log, content-addresses policy versions and does not govern changes to K, and
  disclaims mechanization. Its denial derivation "need not be stored."
- **Zhu & Wang's authorization series** (arXiv:2609.21284, 2610.00347, 2610.00349; September 2026; abstracts read).
  Revocation ordered by **fences and epochs** with a linearized cut after which issuers cannot expand; "durable monotone
  state" across agent replacement, forking and rollback, with exclusion of self-certification; budget conservation
  under crash with **bounded TLA+ model checking**. The nearest the literature has come to ADR-0031's fence and epoch
  and to ADR-0026's "no self-grant," using TOPAK's own tool. Fences are per slot or lineage, not one log; no consensus
  protocol is named; no policy-author threat model; small evaluations. It is also the only work found that models
  delegation chains *and* their revocation (A22), which TOPAK does not.
- **SAGA-BFT** (Laws, Oprea, Nita-Rotaru; arXiv:2605.12364, 2026.05.12; abstract read). Treats the governance
  *service* as Byzantine and puts its decisions through BFT consensus, with monitoring and client-side audit variants.
  The untrusted party is the enforcer, not the author; the shape, consensus over governance decisions because the
  governor may lie, is A9's shape. TOPAK's replicas are crash-recovery, not Byzantine (ToO §12 item 9), so on this one
  axis SAGA-BFT's premise is stronger than TOPAK's.
- **FORGE, "Formal Policy Enforcement for Real-World Agentic Systems"** (Palumbo et al.; arXiv:2602.16708, v3
  2026.05.08). Aspect-oriented instrumentation and a Datalog reference monitor enforcing history-dependent policies
  across multi-agent systems. A third A15 position beside Dogwood's and TOPAK's: a logic-programming store the monitor
  owns. Not mechanized.
- **Mandate** (GitHub, 2026; README read). Task-scoped mandates proposed by an untrusted LLM writer, validated by a
  deterministic checker against a Cedar *ceiling* by language inclusion, with refusals carrying counterexamples and a
  literal that would widen the ceiling "refused rather than translated." ADR-0030's shape for one tier, with no
  governance of the ceiling; phases 3 and 4 not started.
- **AgentCity / NetX** (Ruan; arXiv:2604.07007, 2603.25100; abstracts and summaries only). A constitutional tier
  bounding a legislative tier on an EVM chain, with a reported quorum floor, rotation and conflict-of-interest recusal
  for adjudicators. The only design found whose structure resembles A7, a floor above the rule-makers. It is an agent
  economy, not a reference monitor, and the recusal and quorum text is unverified against the PDF (§12).
- **"Separation of Duties for Privileged LLM Agents"** (Jing; arXiv:2609.38224, 2026.09.28; abstract read). Planner,
  policy gate, executor and auditor as separate roles between agent and OS, approval as a one-shot credential bound
  to the exact bytes that will run, policy changes decided "outside the model through a separated decision layer." SoD
  among runtime roles, not among approvers; no quorum, no formal layer.

**What the scan did not find**, after searching for each of TOPAK's commitments by several names: a policy author
treated as Byzantine; a floor over the approver; authority changes totally ordered on a consensus log with the fence
as the index; erasure modeled as an event with a forensic floor beneath it; a model pinned as weights, prompt and
decoder together; a deny-only detector on a separate fault domain coupled to admission by liveness; a confinement
ladder decided by failure direction with attestation at grant. One paper ("Will the Agent Recuse?", arXiv:2606.06460)
shows that in-band deny signals an agent is asked to honour are model-dependent and unreliable, which is the empirical
case for TOPAK's placement of detection outside the agent.

**The identity standards cluster**, read because A22 runs through it: WIMSE's first working-group AI draft
(`draft-ietf-wimse-aims-00`, 2026.09.15; agents as workloads with SPIFFE identifiers, short-lived credentials, OAuth
for authorization, delegated subject in `sub`); ID-JAG (`draft-ietf-oauth-identity-assertion-authz-grant-04`) behind
Okta's Cross App Access and MCP's stable Enterprise-Managed Authorization extension; the MCP authorization
specification at revision 2026.07.28 (OAuth 2.1, Protected Resource Metadata, Client ID Metadata Documents, Dynamic
Client Registration deprecated, no token passthrough); an individual draft on **attenuating** tokens
(`draft-niyikiza-oauth-attenuating-agent-tokens-01`, 2026.06.15), the only one with a narrow-only-downstream
delegation semantics and tool-argument constraints; A2A v1.0 with hop-by-hop authentication and no delegation
construct. Every one of these assumes an agent will act for another and asks how to attenuate on the way down. TOPAK's
lease binds one principal, one seat and one Persona, and the design has not said whether that is a refusal of
delegation or an omission (§5 item 2).

**The vendor control planes**, one line each, from primary text where marked: HashiCorp Vault 2.1 **ceiling
policies** (the maximum an agent can ever hold, intersected with owner, baseline and per-request RAR; who may change a
ceiling is not described); Google's Agent Gateway with **Semantic Governance Policies** judged by an LLM at runtime,
whose documentation warns that "verdicts may not be accurate," and Model Armor's org-level *floor settings* that
templates cannot weaken; OpenAI Codex's `execpolicy` rule files and an `approvals_reviewer = "auto_review"` option
that routes approvals to an automated reviewer; Cloudflare's Dynamic Workers, where the agent reaches only what the
host bound and the host adds credentials on the way out; Okta's Cross App Access and Auth0's on-behalf-of token
exchange and Token Vault. Taken together: credential custody outside the agent, ceilings above it, and approval as a
configurable step are now the industry's defaults. The approver is configured. In two products it may be a model.

---

## 4. Where TOPAK's design is alone

Each item is a design commitment no surveyed comparable makes, as found on 2026.10.05. Items the 10.01 assessment
listed and the field has since reached are rewritten, not dropped.

1. **The threat is in Build.** Every comparable trusts the policy author: an operator, a console user, a human
   approving the agent's proposal, a configured approver. TOPAK alone treats the author of the policy as Byzantine and
   builds the authority path around that (A6, A7). The field now checks the author's proposal (Progent v3, OpenShell's
   prover, Mandate); it does not doubt whoever accepts it.
2. **A rules floor over a havoc anchor.** No comparable states what bounds the authority that defines who may
   approve. AgentCity's constitutional tier is the one structural analogue and is a blockchain economy, not a runtime
   monitor. TOPAK's regress ends in one axiom bounded by two verified floors.
3. **Classification with routing to a governed approver.** *Rewritten.* Computing what a change adds is no longer
   TOPAK's alone: Progent v3 checks narrowing with Z3 and routes expansions to an approver; OpenShell binds a widening
   to a review token; EBL-Core refuses an operational policy that weakens its root. What is TOPAK's alone is that the
   path a relaxation is routed *to* is itself a principal: a quorum of seats with author/voter disjointness and recusal,
   whose roster the anchor issues and whose anchor the rules floor bounds, with the decision ordered on the log. In the
   comparables the approver is a configuration value, and in two of them it may be set to `auto-approve`.
4. **A total order over authority, and an apply-time re-check against the version decided under.** EBL-Core asks for
   both halves (linearized grant lifecycle, re-check at redemption) and mandates neither a log nor a protocol; Zhu &
   Wang fence per lineage; Temporal fences shards. TOPAK orders grants, revocations, expiries, promotions, issuances and
   erasures in one Paxos log, with the fence as the log index.
5. **Denials as evidence, erasure as a modeled event, and a forensic floor.** OpenShell, AgentCore, AGT, OBPE and
   Mandato record denials; AGT and Mandato chain them. None models what survives erasure, and none separates
   legibility from immutability. ADR-0028's six classes (admit decisions, stop attribution, promotion votes, anchor
   issuances, emergency activations and the calls under them, erasure events) are a design with no counterpart.
6. **Separation of duties as seats, now including the people.** Author/voter disjointness, recusal in the action
   envelope, seat kinds that bound alphabets, and since ADR-0050 (provisional) operators who are principals of a
   fourth kind: a first lease needs a quorum, an add needs a live peer, a deny needs no lease, and "a person who
   operates and also votes is two principals." Jing's architecture separates runtime roles; CaMeL and FIDES separate
   inside one agent; the Five Eyes guidance now *recommends* roles like "Reader" and "Actuator" with consensus
   mechanisms, as practice, without a design. TOPAK separates between principals, enforces it in the envelope, and
   applies the rule to the operator.
7. **Detection with a placement rule, deny-only, and coupled to admission by liveness.** Sentry has a placement and
   no stated rule or direction; the AI-control literature's monitors escalate rather than deny; the Agent Harness's
   evaluator cannot fail open and is in the admit path. No comparable couples admission to a detector's heartbeat.
8. **Confinement as a ladder decided by failure direction**, with attestation at grant and no silent downgrade. One
   research note (Sinet, 2026.07) uses the ladder vocabulary and decides rungs by Meta's Rule of Two, with no
   attestation. Containment runtimes ship one rung.
9. **The model pinned as an artifact** (Persona: weights, prompt and decoder as one promoted identity), with lineage
   independence computed from the log. The IETF PTV draft attests model and policy; Sokolov folds a model measurement
   into a TPM quote; nobody pins the decoder.
10. **Monotonicity stated at sixteen layers** (ToO §7.8, up from fourteen: Ingress and Operation added). The field now
    states it for policy tiers (OBPE, EBL-Core, Progent), labels (FIDES), configuration scopes (Claude Code) and
    privilege sets, each for one object. None states it as a design-wide discipline, and AGT still violates it as a
    feature.
11. **Labels as declarations the mechanism delivers, with handles and no second model.** *New.* CaMeL and FIDES
    reach the planner-never-reads-untrusted-content goal with a quarantined model or a framework-owned variable store.
    TOPAK reaches a weaker form of it with nothing that reads content at all: a label is a function of a declared
    source, a handle is a name the tool host resolves, and the three forbids are in a verified floor. Redpanda's
    out-of-band metadata plane and Google's managed-agent egress proxy are the nearest shapes and carry no labels into
    policy.

---

## 5. Where TOPAK's design is behind or exposed

Design-level only. Every gap that is merely "not built" is excluded; G10 §8 lists those.

1. **No refinement to code (A19).** Unchanged in kind. Stage one, trace validation, is current with the tree (82
   traces, 1,007 steps, every state keeping the abstract confinement invariants) and found the lease-expiry race the
   proofs could not see. Stages two and three, a Lean model with differential testing and then its compilation, are
   "not begun." The reproducible build that would fix the traced binary's identity (T-0045-30) is undeclared. Moon &
   Varshney's design includes the chain; TOPAK's names it.
2. **No delegation model (A22).** *New here.* A principal cannot create a subordinate, so there is no chain, no
   attenuation and no cascade, and no record states whether that is the position. Four reviews have asked (CR-3; gap
   row 1.3). The field is building around chains: WIMSE, ID-JAG, attenuating tokens, Entra Agent ID's delegated
   authority, Zhu & Wang's revocation closure, TACIP 13.2.2's cascading revocation. A deployment with sub-agents has
   nothing to declare against. The cheapest closure is a record that states the prohibition and what a deployment
   that needs sub-agents does instead (one cell per sub-task, each seated by promotion); the expensive one models
   attenuation, and Zhu & Wang's "exclusion of self-certification" and TOPAK's "renewal only narrows" are the same
   rule.
3. **Provenance is per item and per round (A14).** Closed as a gap; stated as a bound. `clearSet` "bounds a round and
   traces no value": once any untrusted item has been delivered clear, every literal the Thinker emits inherits the
   whole round's label set. That is sound and it is blunt, and a deployment that wants finer control has only
   suppression (deliver as a handle), which the record says is the point. CaMeL and FIDES are finer; their cost is a
   trusted interpreter. A label is also a declaration (ToO A15), and the label machinery adds a trust root (ToO §12
   item 18; G10 item 93: the label facts are the deciding replica's, and `apply` re-checks `clearSet` only).
4. **History-dependent policy is fixed folds (A15).** A position, and a real constraint: a deployment wanting "no
   more than N calls to tool T per round" has a mechanism release or unanalyzed Rego, as on 10.01. Dogwood and FORGE
   show the alternative. The record's reason, that a fold added by release is checked with the mechanism and a fold
   policy declares is not, is a good one; it should be stated against Dogwood by name somewhere a reviewer will read it.
5. **No liveness property anywhere.** *New here, from the 10.03 gap assessment (3.1).* Every module is an invariant
   under `Init ∧ □[Next]` with no fairness; Run's posture under a lagging Observer is "stall," and the model cannot tell
   a stall from a deadlock. TACIP 3.2.3's new clause, a refused action part-way through a sequence needs its own
   fail-safe state, is a liveness-adjacent question the formal layer cannot answer. One property under weak fairness
   on the heartbeat would be the first.
6. **The durability cost is still unstated.** ToO §2.4 lists "no shell, no package installation, no network, no git"
   and not "a crashed round loses its work." The 10.01 assessment said this and the 10.03 gap assessment said "the
   statement is owed at the next checkpoint." Temporal, Restate and the harness literature make it the first question.
7. **The operator channel is typed on a provisional record.** ADR-0050 closes CR-34 in design: six requests in schema
   S, nine floor entries, signed, floor-decided, re-checked on apply. Its centre, that a first lease comes from a
   quorum, is not built; at the reference "whoever reaches the socket can seat," and no reader other than the drafter
   has read it. G10 says so in §8. ADR-0052 rests on it, so break-glass has no settled form if either is redesigned.
8. **Replicas are crash-recovery, not Byzantine.** Unchanged, and no longer unique in being visible: SAGA-BFT's premise
   is that the governance service lies. TOPAK declines BFT (ADR-0045) and names the forged admit as the residual; mutual
   authentication, the delegated mitigation, is unbuilt.
9. **The trusted base is long, and longer.** Thirty-six rows, up from thirty-one, five of them for labels and
   operators. Next to Moon & Varshney's five-item sentence it is a design whose audit surface grows with its scope. The
   trade is stated (ADR-0045 §2) and should be stated as a trade in any external text.
10. **Floor fitness has an owner and no test.** The fourth gate the 09.12 assessment asked for is assigned to the
    bootstrap reviewer (ADR-0029 A4, ADR-0030 A3) and "what makes a floor fit is written nowhere." The 09.12
    definition, every privileged effect in the alphabet has a field in the floor's schema and none is discharged by
    abstention, was not adopted and is still the only candidate text. Moon & Varshney's §5.1 proposes the same check
    ("validating that every safety corollary is reachable-non-empty") and built neither.

---

## 6. What the comparables value that TOPAK's axes do not ask about

So that §2 does not read as a scoreboard built by one side:

- **Expressiveness for the agent.** OpenShell, `srt`, Codex, the Agent Harness and AGT keep the shell, the network and
  the package manager. TOPAK's alphabets remove them, knowingly, and the market has chosen the other side in every
  product surveyed.
- **Incremental adoption.** Every comparable can be put in front of an existing agent. TOPAK's guarantees need the
  agent to speak its alphabet and nothing else. The rung-0 `Mediated` path delivers attribution and authorization,
  not containment, and should be described as exactly that.
- **Agent-assisted authoring, checked.** Progent v3, OpenShell's advisor, AgentCore's natural language to Cedar and
  Mandate all let a model write policy and then check what it wrote. TOPAK allows a Build Thinker to `Draft` and routes
  the result through promotion. The comparables' check is cheaper and theirs runs in seconds; TOPAK's is a quorum.
- **Delegation and reach.** The identity standards and the vendor control planes are built for agents that act for
  users and spawn sub-agents across organizational boundaries. TOPAK has one principal per seat and no chain; the
  deployments the field is designing for are the ones TOPAK has not said it can host.
- **Latency.** Unchanged: gateway designs decide in microseconds; TOPAK puts grants, heartbeats and effect admits on a
  consensus log and couples Run's liveness to an Observer.
- **Durability.** Temporal's "a running unit of work survives its worker" is a property TOPAK does not offer and has
  not costed (§5 item 6).

---

# Part II — The external references

## 7. Moon & Varshney, against the text

### 7.1 The paper's status

arXiv:2605.09045, v1 2026.05.09, v2 2026.06.29, 14 pages, cs.AI / cs.CR / cs.SE; no later version. Presented as a
poster at the Second Workshop on Agents in the Wild (AIWILD) at ICML 2026, 2026.07.11, Seoul (confirmed from the
icml.cc workshop page; OpenReview was not reachable). Two citing works (Semantic Scholar): Hu, Goel and Bindschaedler,
arXiv:2609.00430 (runtime refinement for regenerated systems code, PACMI at SOSP 2026), and Oberman, arXiv:2608.14795
(control loss under endogenous influence). No follow-up from either author: no repository, no template-fitness
implementation, no Verus or Lean port, no talk. Enclave Intelligence has a consulting landing page and no research
output. The corpus's caution in ToO §11.1 about citing a workshop paper stands.

### 7.2 Section pointers, verified

The 10.02 review checked three pointers against the PDF. This pass checked every pointer the corpus and the two source
assessments use against the arXiv HTML:

| Use | Corpus / assessment pointer | Verified | Note |
|---|---|---|---|
| Havoc oracle, Listing 1 | §2 | ✓ | `method {:extern} GetActionFromLLM(...)` |
| Soundness theorem | Theorem 3.2, §3.3 | ✓ | Named "Containment Verification Soundness"; premises (A1) abstract havoc safety, (A2) boundary-event refinement |
| Deployed boundary safety | Corollary 3.3, §3.3 | ✓ | Named "Deployed Boundary Safety". **The corollary does not use the phrase "effect exclusivity"**; that is a §5.1 limitation heading. Cite the corollary for the statement and §5.1 for the term |
| Trusted base | §3.4 | ✓ | Five items: Π_I; R and Q; the effect-faithfulness boundary; **the Dafny verifier and compiler**; the extern shim. Z3 and the Python runtime are not named separately |
| "Failure taxonomy" | §3.5 | **✗** | §3.5 is *Mechanization*. Its last paragraph lists three failure sources (failed refinement proof, effect-faithfulness gap, property-completeness gap). There is no section or term "taxonomy". Used in the 09.12 assessment's appendix; check any live text that borrowed it |
| PocketFlow witness, four-variant `Action` | §4.1 | ✓ | |
| Seven-phase pipeline | §4.2 | ✓ | ContainmentSpec, InterfaceContract, GenerateSpec, ValidateSpec, Verify, ClassifyFailure, ProofRepair |
| Information barrier | §4.3 | ✓ | MI(P; I \| R, θ) = 0 by construction |
| Three gates | §4.4 | ✓ | G1 resolution (30 s), G2 vacuity, G3 discrimination |
| Silent abstention | §4.6, Appendix B (B.1–B.3) | ✓ | Both modes pass all three gates (B.3) |
| Deployment stack | Figure 1 | ✓ | Containment layer verified; sandbox, kernel, hardware "operationally audited" |
| Narrow interface | §5 opening | ✓ | "the design pressure shifts from training-time and deployment-time alignment to framework-time interface design" |
| Effect exclusivity, template fitness, witness scope | §5.1 | ✓ | Five limitation paragraphs: effect exclusivity, template fitness, specification fidelity, boundary-enforceable scope, witness scope |
| Guarantee ordering | §2, with Table 1 | ✓ | "S(Empirical) ⊆ S(Distributional) ⊆ S(Universal), with both inclusions typically strict" |
| Scope-declaration model | Impact Statement | ✓ | After §5, before References |

**Confirmed absences**: §4.6 and Appendix B say nothing about human reviewers or correlated human failure; the paper
says nothing about policy change over time, multiple agents, audit logs or who may change the policy; Π_I is a fixed
trusted input throughout.

**Exact wording the corpus may want.** Template fitness: "An additional template-fitness check, validating that every
safety corollary is reachable-non-empty before the final verification attempt, is needed to close this gap." Witness
scope: "The verified guarantee on PocketFlow is at the strength of PocketFlow's four-variant action interface.
Frameworks exposing wider interfaces require correspondingly more proof cases." Impact Statement: "A verified
containment layer is therefore not a complete safety solution. It is a fail safe for a specific class of harms,
intended to compose with oracle-level methods, sandboxing, and statistical certification rather than replace any of
them."

### 7.3 The 09.12 exposures, dispositioned at G10

| 09.12 item | Asked for | At G10 |
|---|---|---|
| I.1 Concordances | State as concordance, not originality | **Done.** ToO §11.1 "Concordant" list, confirmed accurate against the text by the 10.02 review and here |
| I.2 ADR-0010 as the extension to lead with | Floor plus `bundle ⊑ floor` under policy change cadence | **Done and grown.** ADR-0030's composition with a proof checker behind the refinement gate; the rules floor carries the same move to authority; ADR-0047's label minimum is a third instance of "a lower tier cannot loosen" |
| I.3 §4.2 → §4.6 + Appendix B | Fix the citation | **Done in live text**, with one residue: ADR-0024's Consequences still read "fail together (Moon & Varshney §4.6; Knight & Leveson)" and "the floor-fitness gate stay[s] open"; ToO §7.1 is corrected (the human half is Knight & Leveson's alone), ToO A4 states the claim without citation. "§4.2" survives only in struck text and retired-wording lists |
| I.4 Floor fitness, a fourth gate | Define and own it | **Owned, timed, untested.** The bootstrap reviewer ratifies the floor by establishing fitness (ADR-0029 A4; ADR-0030 A3); G10 item 87: "Nothing names what." The 09.12 definition was not adopted. See §5 item 10 and §10 |
| I.5 Adopt Figure 1 as a positioning diagram | State TOPAK's row | **Partly.** ToO §11.1 item 3 restates the sandbox gap in the paper's vocabulary and item 5 notes Figure 1 covers Run only; ADR-0034's rungs give the row structure the figure lacks. No diagram carries it (G10 item 76: the diagrams are not measured and behind the tree) |
| I.6 `Contained`/`Mediated` as theorem vs corollary | Recut the inventory | **Not adopted.** ToO §2.3 keeps "safety theorems quantify over `Contained`"; §11.1 item 4 lists the alignment as an exposure with no resolution. Still the cleanest available sentence for why a `Mediated` human loses exactly the deployment-closure step and nothing else |
| I.7 Trusted base enumeration | A §3.4 analogue | **Done, at scale.** ADR-0045: 36 rows in four classes (26 trust roots, 4 delegated, 4 excluded, 2 mixed; the refused class is currently empty), Annex A for the archetype and Annex B for the reference; the paper's verifier appears as T-0045-31 with a certified configuration |
| I.8 TLC versus TLAPS | Declare which | **Done.** ADR-0046 §1: TLC at small constants for existential claims, TLAPS for universal ones; "proved" reserved for the latter. 22 modules, 5,225 obligations, 19 certified through cvc5 and the `ethos` checker; LS4 steps and the prover's translation stay trusted |
| Varshney spelling | Sweep | **Done.** "Varney" survives only in the 09.12 document's own correction note |
| Scope-declaration paragraph | The Impact Statement analogue | **Not written.** ToO §13 is assumptions of use; `architecture-description.md` has an "out of scope by position" line and a characteristics table. The 10.03 inventory's 28 X rows "each still need a scope declaration, and ToO §13 is where most would land" |

### 7.4 Where the comparison stands

**Concordant**, as before. **Extended**, further: policy change, authority above the operator, the record, multiple
agents, operators as principals, and now labels at ingress, none of which the paper has. **The verifier is declared
and certified** where the paper's is trusted: the paper's §3.4 names the Dafny verifier and compiler and accepts them;
TOPAK's T-0045-31 names its prover, pins its binary and backs nineteen of twenty-two modules with proofs an
independent checker accepted. **Still behind** on the one artifact that defines the paper: the chain to code. And
**the two still agree on the open problem**: the fourth gate, named by the paper as template fitness and by TOPAK as
floor fitness, built by neither; in TOPAK it now has an owner who does not yet exist and a definition nobody has
written.

One asymmetry the 10.02 review named is sharper now. The paper's §5.1 cautions that wider interfaces need more proof
cases. TOPAK's typed surface is nine action variants across two domains, six operator requests, nine control entries
and an emergency seat kind, and its floor is 28 policies with 107 cases, up from 17. The surface the paper would ask
to see typed is now typed; it is also three times the size it was, and every new case is one hand's.

---

## 8. NIST, TACIP, and the frameworks that appeared around them

### 8.1 The AI RMF and the Playbook: unchanged

The AI RMF 1.0 "is being revised as part of the White House AI Action Plan"; no 1.1 draft, version or timeline is
posted. The Playbook page says it "will be updated after the AI RMF is revised," and nothing has been published in
2026. **The 72-subcategory Playbook the 10.03 inventory marks is the current one, and the inventory stands as basis.**
One relabelling to expect: Executive Order 14434 (2026.09.29) directs agencies to say "Super Intelligence" for "AI" in
non-statutory material, and NIST's ITL program page already does; document numbers (AI 100-1, 600-1) are unaffected.

**What G10 would move in the inventory.** The 10.03 inventory marks G9 (M 11 · P 24 · C 4 · G 5 · X 28). This is a
reading against G10, not a re-marking; the next inventory should carry it:

| Row | At G9 | What G10 adds | Direction |
|---|---|---|---|
| GOVERN 2.1 Roles, separation of duties | M | Operators are principals who observe each other; "a person who operates and also votes is two principals" (ADR-0050, provisional) | Strengthened |
| GOVERN 1.7 Decommissioning | P | A deny needs no lease; a domain with no live operator stalls until a quorum seats one | Strengthened on the principal half |
| MAP 3.4 Operator proficiency | G | An operator is a principal with a Persona, a key and a provider; nothing about skill | G, unchanged, and now the only place the gap could sit |
| MAP 2.3 Scientific integrity / TEVV | M | Proof certification (19 of 22 modules) and trace validation current with the tree | Strengthened |
| MEASURE 2.13 Effectiveness of TEVV | G | Floor fitness owned and timed (ADR-0029 A4; ADR-0030 A3); no test | G, with an owner |
| MEASURE 3.2 Risk tracking without metrics | G | Unchanged; `L` unmeasured; placeholders unmeasured; the correlator (ADR-0051) would count misses and is Proposed | G |
| MEASURE 1.3 Independent assessors | G | 28 confirmation-required records, two provisional; the A2.5 line carried for the first time: "Bootstrap reviewer engaged: None" | G, and larger |
| MANAGE 2.4 Supersede, disengage, deactivate | M | Break-glass is an emergency seating for one round with no TTL; X1 retired; the floor's exceptions are one; an emergency seat is not coupled to an Observer | Strengthened; the 09.12 contradiction stays gone |
| MANAGE 1.4 Residual risk | G | Written 2026.10.03; numbers undeclared; predates G10 on floor fitness, R8, ADR-0005 and the row count | P on the next re-marking, and due for a refresh |
| MANAGE 3.1 Third-party risk | P | Operators' identity providers are trusted-base rows (T-0045-35, 36); independence between providers is an archetype rule | Strengthened; still no monitoring |
| MANAGE 3.2 Pre-trained model risk | P | Unchanged | P |
| MAP 3.2 Costs and benefits | C | The durability cost is still not stated | C, unchanged |

**Reverse deltas** the 10.03 inventory lists (passive e-stop, monotonicity across layers, floor refinement at promotion,
evictability, HOOTL, `Contained`/`Mediated`, Build as the hostile domain, a computed theorem inventory) gain one:
**labels as declarations delivered by the mechanism**, which no Playbook row and no TACIP implementation describes.

### 8.2 TACIP: the 2026.09.28(a) draft

The 10.02 review graded the 09.13(b) draft. The repository holds 09.28(a) at `doc/`, which its own changelog calls "a
minor update": one Task, six Implementations and a section on using the profile added; no Practice, Task or
Implementation removed; thirteen Practices as before. A community-of-interest participant's public timeline dates a
"Discussion Draft 3" to 2026.09.22; whether that is the 09.28(a) text or an intermediate one could not be determined,
since drafts are distributed on the COI list and Slack only (§12). Nothing newer is known.

The 10.02 grade (B+) stands; the profile's technical asks did not move. Six changes land on TOPAK by name:

| 09.28(a) change | TOPAK |
|---|---|
| **3.2.3**: a refused action part-way through a sequence needs its own fail-safe state, with a pump-changeover example | TOPAK refuses and records; the round continues or ends at its bound; nothing models a compensating action, and the formal layer has no liveness property to say whether "stall" is the fail-safe state or a deadlock (§5 item 5). A deployment under TACIP would declare its answer per effect class, and ADR-0023's schema has no field for it |
| **2.2.2**: "a watchdog may itself be part of the attack surface" | The Observer is the watchdog. Coupling makes its absence loud and cannot see its collusion (ToO A13); lineage independence is the only cover and is Proposed. TACIP has now said the thing the corpus says about itself |
| **3.9.5(c)**: "the organization can confirm the change actually took effect, rather than relying exclusively on the capability's self-attestation" (unchanged wording; **6.1.5** now adds that vendor self-attestation "should not be treated as sufficient to suppress a warning") | Every liveness fact inside the mechanism is the Observer's own heartbeat and watermark; gate evidence is an operator's assertion (T-0045-13, G10 item 57); the corpus itself is self-attested by its author. *Verifiable* still fails, as the 10.02 review scored it |
| **10.1.2**: the inference receipt "can also record the rules or branches that were applied" | The floor deny names its forbids (ADR-0030 R4); the `Actuate` record carries labels, delivery mode and `clearSet`; the lease names the bundle revision. TOPAK's receipt already records the rules applied, and the 10.02 review's tension stands: TACIP also wants prompts and context, which TOPAK keeps in a store built for deletion |
| **7.5** now applies to changes "in its prompts, retrieval corpus, or guardrails" without a model change | A Persona pins prompt and decoder with the weights (ADR-0016); a bundle or floor change is promoted and classified. TACIP's "re-assess the update" is TOPAK's "route the change"; the difference is who decides |
| **Scope**: the profile applies zero trust "to a legitimate, uncompromised AI system that is not behaving as intended"; "language incorrectly implying guarantees removed" ("ensures" → "helps ensure") | The havoc premise, stated by a regulator, and the register discipline the 10.02 review graded TOPAK on (CR-25) adopted by the profile itself |

### 8.3 The rest of NIST's agent work

- **The AI Agent Standards Initiative** (CAISI, 2026.02.17): industry-led standards, open protocols, research on agent
  security and identity; an RFI with ~400 responses; "Agent Security guidelines" listed as upcoming and unpublished.
- **The NCCoE agent identity and authorization concept paper** (2026.02.05) and its summary of 600+ comments: agent
  identity is "a combination of the agent's workload or service identity, its operating instance, the human or
  organization that authorized it, and the specific authority it holds at a given moment"; evidence must show "what
  request was evaluated, what decision was returned, what identities and delegations were relevant [and] whether an
  approval occurred"; commenters asked for "a logically separate agent governance component." Every clause is one
  TOPAK's lease, record and mechanism discharge, and the paper "does not provide specific details about formal approval
  workflows, change management processes, or designated policy change authority." The hypothesized stack is OAuth 2.0,
  SPIFFE/SPIRE and MCP, which is the delegation cluster of §3.9.
- **COSAiS** (SP 800-53 overlays): single-agent and multi-agent overlays are listed; only the predictive-AI outline has
  been published. **IR 8596** (Cyber AI Profile): preliminary draft only. **AI 800-4** (monitoring deployed systems,
  March 2026): six monitoring categories, no change-control content. **AI 100-2 E2025** added agent attack categories;
  no 2026 edition.
- **CAISI's agent-hijacking competition** (2026.03.23, with Gray Swan and UK AISI): every frontier model was
  successfully attacked at least once, and universal attacks transferred across models. Measurement, not controls;
  the empirical case for the havoc premise and for labels that bound what a successful injection can reach.

### 8.4 OWASP Top 10 for Agentic Applications (2026)

Released 2025.12.09 by the Agentic Security Initiative; read from the PDF. It is the first widely used list that
describes TOPAK's threat in its own words, and the mapping is short:

| ASI | TOPAK |
|---|---|
| 01 Agent goal hijack | Not prevented; bounded. Havoc premise; labels bound what a hijacked Thinker can reach (ADR-0047); its mitigation 3, "changes to goals or reward definitions must go through configuration management and human approval," is promotion |
| 02 Tool misuse | Floor ∧ ¬bundle per lease; "outward" derived, never declared; the purpose text is still a claim |
| 03 Identity and privilege abuse | Lease, Persona, operator as principal; "without a distinct, governed identity of its own, an agent operates in an attribution gap" is ADR-0031's premise. Delegation chains, the item's main subject, are absent (§5 item 2) |
| 04 Agentic supply chain | Artifact digests, pinned Personas, a tool's interface through promotion, 36 trusted-base rows; the model provider is a row, not an event |
| 05 Unexpected code execution | No shell in either alphabet; the rung ladder; no real principal `Contained` |
| 06 Memory and context poisoning | A round is the unit; `clearSet` is the only memory policy reads; persistent agent memory is outside the pattern and should be declared so |
| 07 Insecure inter-agent communication | No agent-to-agent protocol; cells communicate through the record; A2A absent by construction |
| **08 Cascading failures**, including "governance drift cascade: human oversight weakens after repeated success; bulk approvals or policy relaxations propagate unchecked" | **The one item that names TOPAK's premise.** A relaxation is computed, routed to a quorum and ordered; a bulk approval is a sequence of grants on the log; an operator's successor grant can only narrow |
| 09 Human-agent trust exploitation | HOTL with a budget (`W + L + D < T_irrev`); operators coupled to a peer's presence, "not to anything the peer has read" |
| 10 Rogue agents: "immutable and signed audit logs of all agent actions, tool calls, and inter-agent communication" | The consensus-ordered record with denials; bundle signing (under a throwaway key); gate evidence unsigned (item 57) |

### 8.5 EU, ISO, CSA, Five Eyes, and the question nobody asks

- **EU AI Act.** Agents are not a category: "the definitions of an AI system in Article 3(1) and of a GPAI model in
  Article 3(63) are sufficient to cover AI agents"; Art. 50 transparency from 2026.08.02; the Digital Omnibus (in force
  2026.07.27) defers Annex III obligations to 2027.12.02. Standards for Art. 12 logging and Art. 14 oversight are
  prEN 18229-1 and -3 (CEN-CENELEC JTC 21, enquiry 2026), with no agentic deliverable. **ISO/IEC SC 42**: 42001
  unamended; 42005 and 42006 published; a 36-month scoping item on human-machine teaming and agents; no TR.
- **CSA**: MAESTRO (threat modeling), Agentic AI IAM (DIDs, VCs, a Policy Administration Point with no statement of who
  may set policy), the Agentic Trust Framework (promotion through tiers by "explicit approval from authorized
  stakeholders," no governance of the policy itself), and a draft "NIST AI RMF: Agentic Profile" with autonomy tiers and
  accountability registers.
- **Five Eyes, "Careful adoption of agentic AI services"** (ASD's ACSC, CISA, NSA, the Canadian Cyber Centre, NCSC-NZ,
  NCSC-UK; 2026.05.01; 29 pages, read from the PDF the custodian placed at
  `doc/careful_adoption_of_agentic_ai_services.pdf`). It is the one government text in this survey whose recommended
  practices read like TOPAK's records, and it should be cited by name in any external draft. Verbatim, from its
  developer, deployment and operation sections:

  | Five Eyes practice | TOPAK |
  |---|---|
  | "Codify separation of duties by defining roles, such as 'Orchestrator', 'Reader' and 'Actuator' with clear boundaries, consensus mechanisms and delegations expiry" | Seat kinds that bound alphabets (ADR-0037); promotion as a quorum grant; the lease's round bound. The three roles named are, near enough, Build's `Draft`/`Submit`, Run's `Consult` and Run's `Actuate` |
  | "Implement consensus controls for actions based on risk; use multi agent approval for moderate stakes actions and human in the loop approval in addition to multi agent consensus for high stakes actions" | Promotion (a quorum of seats) for authority changes; `W + L + D < T_irrev` per effect class decides where a human fits. TOPAK applies consensus to *authority*, not to each action; the guidance asks for it per action by stakes |
  | "Prohibit agents from modifying their own privileges or initiating unapproved delegation without explicit expiry timers and recorded grant chains" | No self-grant (ADR-0026; ADR-0050's "a key by itself is not a standing lever"); every grant on the log; the lease's `ttl`. **Delegation is the half TOPAK has not written** (§5 item 2): the guidance assumes chains and asks that they be recorded and expire; TOPAK has no chains and no record saying so |
  | "Standardise tool descriptions using a consistent format that avoids persuasive language"; misleading descriptions "can cause agents to select tools unreliably" | ADR-0048 and ADR-0049: the interface is part of the promoted entry, rendered by the mechanism, "the only description with standing" |
  | "Establish trigger-action protocols that automatically restrict agent permissions when unexpected behaviour emerges"; "reduce trust levels when anomalous behaviour is detected" | Deny-only detection (ADR-0038, ADR-0039): findings subtract and never add. The guidance's trust score moves *down* on anomaly; it does not say it may move up, which is the direction AGT takes and TOPAK refuses |
  | "Ensure decisions about when human approval is required are determined by system designers or operators, not delegated to the agentic AI system" | ADR-0007's placement: nothing a model says enters the admit path; where a human sits is a floor and bundle matter |
  | "Quarantine requests to delete logs or audit records until reviewed and approved by a human" | Erasure as a consensus-ordered event with a roster (ADR-0006), and the six classes no erasure reaches (ADR-0028) |
  | "Isolate agents into enclaves with no write access to logs" | A principal writes nothing to the record; the mechanism writes admits, denials and seals on its behalf (ADR-0020) |
  | "Require agents to perform cryptographic attestation where agents must prove that they are running expected and unmodified code" | Rung 3 (ADR-0034), designed and SIMULATED; the Persona pins the model as an artifact |
  | "Apply cryptographic integrity checks for task definitions and constraints"; "Authenticate agents with fresh cryptographic proofs before every privileged call" | The task's digest and label on the log (ADR-0050); the lease and its fence compared on every admit |
  | "Deploy a secondary agent to validate new tasks against policy before execution" | The one practice TOPAK would place differently: a second agent in the admit path is semantic lift; TOPAK's second agent is the Observer, out of path and deny-only |

  The guidance's regress ends where everyone's does: "human in the loop approval" for high-stakes actions, and "clearly
  assign responsibility and accountability." It does not say who may change the policy the consensus controls enforce,
  or how many must agree.
- **Who may change the policy.** Across everything read, from NIST to OWASP to the EU to CSA to the Five Eyes: change
  control over goals and permissions is asked for (OWASP ASI01, ASI02), consensus over actions is asked for (Five
  Eyes), logging of policy changes is implied, and separation of duties between the author of a policy and its approver
  is stated nowhere. The regress ends in "human approval" in every text, and no text asks which human, how many, or
  what bounds them.

---

# Part III — What to do with this

## 9. Design ideas worth considering

None of the following is decision text. Each names the record it would touch. Items from the 10.01 list that G10
closed are struck; the rest are carried or new.

1. ~~Provenance labels as a syntactic lift.~~ **ADR-0047**, in force. The residue is §5 item 3 and G10 item 93.
2. **State the A15 position against Dogwood by name.** ADR-0047 R13 and ADR-0030 A2 decide that history reaches policy
   as mechanism folds. A sentence in ToO §3.1 or §2.10 saying *why not an MFOTL layer* (a fold added by release is
   checked with the mechanism; a fold policy declares is analyzed by nothing) would pre-empt the first question a
   reader who knows Dogwood will ask. Narrative only.
3. **Temporal as a delegated substrate, with the boundary stated.** Carried from 10.01, unchanged: an ADR-0045 Annex
   row (delegated, for durable waits and timers) and a refusal (any workflow logic on the admit path), with the admit
   as the unit of retry and at-least-once retry fenced by the admit's log index. Nothing in any record yet. The Agent
   Harness's "a handler that can move the guardrail must never become a tool a driving model can call" is the same
   rule as ADR-0045's refused class and could be cited.
4. ~~Pin tool descriptions with the tool.~~ **ADR-0048 and ADR-0049**, in force, by a different route. One residue
   worth a sentence: the entry's digest does not cover the interface, labels or channel, which ride on the bundle
   revision and signature (ADR-0049 §2, considered and declined). A reviewer who expects a per-tool digest should find
   the reason in the record, and does.
5. **Correct the live miscitation in ADR-0024.** Its Consequences still cite "Moon & Varshney §4.6; Knight & Leveson"
   for correlated human failure and say the floor-fitness gate "stay[s] open." The first is the error the 10.01
   assessment and the 10.02 review found and ToO §7.1 fixed; the second is stale since Batch 34. An erratum or an
   amendment at the next batch. Also retire "failure taxonomy (§3.5)" wherever it survives; the paper has no such
   section.
6. **State the durability cost beside the capability cost** (ToO §2.4). Carried from 10.01 and the 10.03 gap
   assessment; owed since G7.
7. **A positioning sentence in ToO §1.** Carried. §1 states the inversion and does not say the inversion is what
   separates TOPAK from the field. With Progent v3, OpenShell's review tokens and OBPE on the shelf, the sentence can
   now be sharper than it could on 10.01: *the field checks the author's proposal; TOPAK governs the approver.*
8. **A delegation record, in one of two forms.** *New.* Either the prohibition as a position (one seat per principal,
   no subordinates; a deployment that needs sub-agents seats each by promotion into its own cell) with the
   consequence stated for TACIP 13.2.2 and OWASP ASI03, or an attenuation model, for which Zhu & Wang's revocation
   closure and `draft-niyikiza-oauth-attenuating-agent-tokens` are the two texts to read first. ADR-0037 §1 and
   ADR-0031 would carry it. This is the gap the field makes most visible and the one four reviews have asked about.
9. **One liveness property.** *New here.* Weak fairness on the Observer heartbeat in `Coupling.tla`, so the model can
   distinguish "stalled, and will proceed when the Observer returns" from deadlock. It would also give TACIP 3.2.3 an
   answer. `spec/proof-method.md` §5 is where the method would change.
10. **Write the floor-fitness test, or adopt the 09.12 one.** The 09.12 assessment's definition (every privileged
    effect reachable through the alphabet has a field in the floor's schema; no effect is discharged by abstention) is
    decidable under ADR-0007 for the reason `bundle ⊑ floor` is, and Moon & Varshney §5.1 proposes the same check
    as "reachable-non-empty." ADR-0030 A3 names who and when; a short text naming *what* would let the bootstrap
    reviewer do more than attest.
11. **A scope-declaration paragraph**, carried from 09.12 and never written: the TOPAK-shaped analogue of the paper's
    Impact Statement, naming MAP and MEASURE as out of scope by position and the 28 X rows as the inventory of what
    is declared out. ToO §13 or a new §13a.
12. **The deployment declaration gains two fields**: a fail-safe posture per effect class for a refused action
    mid-sequence (TACIP 3.2.3) and a TACIP 8.2 position on root-cause analysis (the 10.02 review's CR-38). ADR-0023's
    schema.

---

## 10. Consolidated open items generated by this assessment

| Item | Placement | Priority | From |
|---|---|---|---|
| ADR-0024 miscitation and stale "stays open" | ADR-0024 erratum or amendment | **Blocking for any external draft** | §7.3, §9 item 5 |
| "Failure taxonomy §3.5" pointer | Wherever live; the 09.12 appendix is frozen | Blocking for any external draft | §7.2 |
| Delegation: prohibition as position, or an attenuation model | New record; ADR-0037, ADR-0031 | **High** | §5 item 2, §9 item 8 |
| Floor-fitness test text | ADR-0030 A3; ADR-0029 §5 step 6 | **High**, carried since 09.12 | §5 item 10, §9 item 10 |
| Durability cost stated | ToO §2.4 | Medium, carried since 10.01 | §5 item 6 |
| A15 position stated against Dogwood | ToO §2.10 or §3.1 | Medium | §9 item 2 |
| One liveness property | `spec/Coupling.tla`; `proof-method.md` §5 | Medium | §5 item 5, §9 item 9 |
| Temporal / durable execution as a delegated substrate | ADR-0045 Annex row | Medium, carried since 10.01 | §9 item 3 |
| Positioning sentence | ToO §1 | Medium, carried since 10.01 | §9 item 7 |
| Scope-declaration paragraph | ToO §13 | Medium, carried since 09.12 | §9 item 11 |
| Deployment declaration: TACIP 3.2.3 and 8.2 fields | ADR-0023 §6 | Low-medium | §9 item 12 |
| Re-mark the Playbook inventory at G10 | A new derived inventory | Low; the rows that move are in §8.1 | §8.1 |
| Refresh the residual-risk statement for G10 | A new derived statement | Low-medium; it predates G10 on four facts | §8.1 |
| Cite the Five Eyes guidance in ToO §11 beside the Playbook and TACIP | ToO §11; `doc/` holds the PDF | Low-medium; it is the governance text nearest the records | §8.5 |
| `Contained`/`Mediated` as theorem vs corollary | ToO §2.3 | Low; a narrative gain, no design change | §7.3 |

**What this assessment does not add to the open list**: the sandbox gap, the refinement chain, independent review, the
operator design's evidence, break-glass's settled form, the correlator, the replicas. G10 §7 and §8 carry all of them,
and nothing found in the field changes their priority. The field's own state makes one of them louder: the
confinement ladder is still the only design in the survey that says which host failures it tolerates, by direction,
and it is built at the rung where the host is trusted.

---

## 11. Summary table: how each design answers TOPAK's three questions

| | *What may the agent do?* | *Who may change that, and how is the change classified?* | *What record survives?* |
|---|---|---|---|
| **TOPAK** | Alphabet ∩ floor ∩ ¬bundle, per lease; labels bound what an injected Thinker can send outward | Byzantine authors; computed classification routes to promotion or anchor + promotion; the rules floor bounds the anchor; operators keep a quorum's grant going and may only narrow it (provisional) | Ordered admits, recorded denials, six non-erasable classes, erasure modeled; the round's tool list and labels on every `Actuate` |
| Moon & Varshney | Verified policy at the typed boundary | Not addressed; one fixed policy | Not addressed |
| OpenShell | YAML/Rego over FS, process, L4–L7, per binary | Operator; agent may propose; prover computes added reach and binds it to a review token; CAS on revisions (draft) | OCSF events, attributed denials; agent output kept out of status |
| Temporal (+ Harness) | Whatever worker code does; Harness: allow-list ∪ evaluator ∪ human | Whoever deploys the worker; Harness guardrails not model-callable | Accepted events with a server-stamped principal; not rejections |
| AgentCore + Dogwood | Cedar (+ MFOTL over a caller-named session) at the gateway | Console; natural language to Cedar; a change invalidates sessions | Gateway logs and metrics |
| CaMeL / CaMeLoT | Plan ∩ capability policy; plan model-checked | Policy author, unaddressed | Not addressed |
| FIDES | Label-lattice policy before tool calls; MCP labels restrict only | Developer | Audit log per session |
| MS AGT | Policy ∩ trust-score ring | Operator; score moves with behavior | Hash-chained decisions with `policyVersion` |
| Progent v3 | Generic ∩ task rules per tool | LLM proposes; Z3 says narrows or not; narrowings apply, expansions go to a configured approver | Not addressed |
| OBPE | Owner ceiling ∩ agent restriction, Cedar, at the tool boundary | Named owners, "future work" | Every decision an audit record |
| EBL-Core | Root ∩ operational, non-weakening; grants linearized | Content-addressed versions; root changes ungoverned | Denial derivations, optional |
| `srt` / Claude Code | Domain allowlist; managed scope cannot be widened by project scope | Managed settings; masking only from trusted scopes | Violation log with attribution |

Everyone answers the first question. More answer the third than did on 10.01. Three now compute something about the
second: Progent what a revision adds, OpenShell what a proposal adds, EBL-Core whether an operational policy weakens
its root. Only TOPAK governs the person the second question ends at.

---

## 12. What could not be verified, and how each comparable was read

- **Moon & Varshney**: arXiv abstract page and HTML v2 (primary); the PDF at `doc/2605.09045v2.pdf` is the same
  version. Appendix B read as a detailed paraphrase (the extractor declined to return it verbatim); every section
  pointer in §7.2 was checked against the HTML. OpenReview unreachable; acceptance confirmed from icml.cc. Citation
  count from Semantic Scholar (2) and alphaXiv (0); Google Scholar not fetched.
- **OpenShell**: repository commits, PRs, releases and `rfc/` through the GitHub API, 2026.10.01 → 10.05 (primary).
  Sentry: the 09.28 blog only. The nvidianews release returned an excerpt.
- **Anthropic**: `sandbox-runtime` commits and README, Claude Code sandboxing documentation and changelog (primary);
  the engineering posts on containment (primary, not design specifications).
- **Temporal**: `docs.temporal.io/handling-messages` for the validator sentence (primary); Agent Harness repository and
  README (primary); Replay 2026 and changelog (official blog). **Restate, DBOS**: blog posts and documentation; the
  Restate blog index and one DBOS URL failed.
- **AgentCore, Dogwood**: AWS documentation pages (`policy`, `policy-core-concepts`, `policy-enforcement-modes`,
  `policy-temporal`) and the Dogwood repository and guide index (primary). `policy-create-policies` and
  `policy-advanced` were not read, so a policy-version field there cannot be ruled out.
- **CaMeLoT**: arXiv abstract (primary). **FIDES**: Agent Framework security page, `ms.date` 2026.10.05 (primary).
  **AGT**: README, `docs/ARCHITECTURE.md`, CHANGELOG (primary). **Entra Agent ID**: Learn page (primary); Agent 365 dates
  secondary.
- **Progent v3**: arXiv HTML (primary). **AgentSpec**: arXiv v3 (primary). **Invariant / Agent Scan**: READMEs and
  CHANGELOG (primary); source not inspected for whether hash-pinning code remains.
- **MCP**: specification revision 2026.07.28, `ext-auth` repository, SEPs through the GitHub API (primary). **IETF**:
  datatracker API per draft (primary). **A2A**: specification text (primary); release date secondary.
- **New papers (§3.9)**: OBPE and EBL-Core full text; Zhu & Wang, SAGA-BFT, FORGE, Jing at abstract level; Mandate
  from its README; **AgentCity's quorum, rotation and recusal text is from search summaries and unverified against
  the PDF.** The §3.9 "vendor control planes" lines are from vendor documentation or blogs as marked in the agent
  reports; Google Agent Gateway's `DRY_RUN` is from release-note summaries.
- **NIST**: nist.gov, csrc.nist.gov, airc.nist.gov, pages.nist.gov and the March 2026 VCAT deck (primary). **TACIP**:
  the 09.28(a) draft from `doc/` (primary); its dating relative to a "Discussion Draft 3" of 2026.09.22 rests on one COI
  participant's site. No draft text is public. **OWASP**: the PDF (primary). **EU**: the AI Act Service Desk FAQ
  (primary); Omnibus and JTC 21 dates secondary. **ISO, CSA**: secondary except the CSA IAM and ATF pages.
- **Five Eyes "Careful adoption of agentic AI services"**: 403 from media.defense.gov and no text on the CISA landing
  page; read from the PDF the custodian supplied at `doc/` (29 pages, text extracted with pypdf). Every clause in §8.5
  is verbatim from it. Its publication date (2026.05.01) is from the NSA and CISA release pages, not the PDF, which
  carries no date in its extracted text.
- **The landscape scan** (§3.9) ran about thirty searches over arXiv, GitHub, IETF, OpenID and vendor sites and
  fetched about thirty-five primary pages; it did not crawl arXiv listings exhaustively, and an October paper on
  policy-change governance could have been missed.
- **Not included**: closed agent platforms with no public design text; Sokolov's AEP/RATS composition
  (arXiv:2608.00801; `draft-sokolov-rats-aep-composition-06`, 2026.08.31), a record-attestation design that remains
  the natural comparable for a future note on ADR-0028's archive; the AI-control literature (Redwood, UK AISI), whose
  monitors escalate rather than deny and are better compared against ADR-0051 when it is in force.

---

## Sources

**TOPAK.**
- `checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md`
- `narrative/theory-of-operation.md` (revision 14): §1, §2.3, §2.4, §2.10, §3.1–§3.3, §4, §7.8, §7.10, §11, §12, §13
- `decisions/ADR-0007.md`, `0013`, `0015`, `0020`, `0023`, `0024`, `0028`, `0029`, `0030`, `0031`, `0032`, `0034`, `0035`,
  `0037`, `0039`, `0045`, `0046`, `0047`, `0048`, `0049`, `0050`, `0051`, `0052`
- `floor/proposed/emergency-floor.cedar`; `floor/genesis-values.json`
- `derived/topak-competitive-design-assessment-2026.10.01.md`; `derived/topak-external-assessment-2026.09.12.md`;
  `derived/topak-critical-review-2026.10.02.md`; `derived/topak-playbook-delta-inventory-2026.10.03.md`;
  `derived/topak-design-gap-assessment-2026.10.03.md`; `derived/topak-residual-risk-statement-2026.10.03.md`;
  `derived/topak-vs-nvidia-open-agent-safety-platform-2026.09.28.md`
- `doc/2605.09045v2.pdf`; `doc/DiscussionDraft_NIST_AIRMF_TACIP_20260913b.md`; `doc/DiscussionDraft_NIST_AIRMF_TACIP_20260928a.md`;
  `doc/careful_adoption_of_agentic_ai_services.pdf`

**Moon & Varshney and related.**
- [arXiv:2605.09045](https://arxiv.org/abs/2605.09045) · [HTML v2](https://arxiv.org/html/2605.09045v2) ·
  [AIWILD at ICML 2026](https://icml.cc/virtual/2026/workshop/54082)
- Citing: [Hu, Goel, Bindschaedler, arXiv:2609.00430](https://arxiv.org/abs/2609.00430);
  [Oberman, arXiv:2608.14795](https://arxiv.org/abs/2608.14795)
- Related verification: [Lean4Agent, arXiv:2606.06523](https://arxiv.org/abs/2606.06523);
  [Metere, arXiv:2605.23951](https://arxiv.org/abs/2605.23951); [FORGE, arXiv:2602.16708](https://arxiv.org/abs/2602.16708)
- [Sokolov, arXiv:2608.00801](https://arxiv.org/abs/2608.00801);
  [draft-sokolov-rats-aep-composition](https://datatracker.ietf.org/doc/draft-sokolov-rats-aep-composition/)
- [Ron, Baudry, Monperrus, N-Version Programming with Coding Agents, arXiv:2606.20158](https://arxiv.org/abs/2606.20158)
  (Knight & Leveson revisited with agents)

**OpenShell, Anthropic, Temporal, Restate, DBOS.**
- [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell): PRs
  [#3110](https://github.com/NVIDIA/OpenShell/pull/3110), [#3785](https://github.com/NVIDIA/OpenShell/pull/3785),
  [#3923](https://github.com/NVIDIA/OpenShell/pull/3923), [#4005](https://github.com/NVIDIA/OpenShell/pull/4005),
  [#4171](https://github.com/NVIDIA/OpenShell/pull/4171), [#4217](https://github.com/NVIDIA/OpenShell/pull/4217),
  [#4219](https://github.com/NVIDIA/OpenShell/pull/4219); `rfc/`
- [Open Agent Safety Platform technical blog](https://developer.nvidia.com/blog/nvidia-open-agent-safety-platform-a-reference-for-continuous-in-silicon-agent-monitoring/)
- [anthropics/sandbox-runtime](https://github.com/anthropics/sandbox-runtime);
  [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing);
  [sandbox environments](https://code.claude.com/docs/en/sandbox-environments);
  [Agent SDK secure deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment);
  [How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)
- [Temporal: Update validators](https://docs.temporal.io/handling-messages);
  [Agent Harness](https://github.com/temporal-community/temporal-agent-harness);
  [Replay 2026 announcements](https://temporal.io/blog/replay-2026-product-announcements);
  [Principal Attribution](https://temporal.io/changelog/workflow-execution-with-principal-attribution-pre-release)
- [Restate: updating agents safely](https://restate.dev/blog/dealing-with-versioning-in-long-running-agents);
  [DBOS authentication and authorization](https://docs.dbos.dev/python/tutorials/authentication-authorization)

**Policy and data-flow comparables.**
- [AgentCore Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html);
  [temporal policies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-temporal.html);
  [Dogwood blog](https://aws.amazon.com/blogs/opensource/introducing-dogwood-runtime-verification-for-ai-agents/);
  [dogwood-policy/dogwood](https://github.com/dogwood-policy/dogwood)
- [CaMeL, arXiv:2503.18813](https://arxiv.org/abs/2503.18813); [CaMeLoT, arXiv:2609.18674](https://arxiv.org/abs/2609.18674)
- [FIDES in Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/security);
  [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit);
  [Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id)
- [Progent v3, arXiv:2504.11703](https://arxiv.org/abs/2504.11703); [AgentSpec, arXiv:2503.18666](https://arxiv.org/abs/2503.18666)
- [invariantlabs-ai/invariant](https://github.com/invariantlabs-ai/invariant);
  [Snyk Agent Scan](https://github.com/invariantlabs-ai/mcp-scan)
- [Meta: Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/);
  [Google Semantic Governance Policies](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/semantic-governance-overview);
  [OpenAI guardrails and approvals](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals);
  [Cloudflare Dynamic Workers](https://blog.cloudflare.com/dynamic-workers);
  [HashiCorp Vault agentic IAM](https://www.hashicorp.com/en/blog/announcing-native-ai-agent-support-in-hashicorp-vault);
  [Okta Cross App Access](https://www.okta.com/blog/ai/ai-security-agent-cross-system-trust/)
- [MCP authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization);
  [MCP ext-auth](https://github.com/modelcontextprotocol/ext-auth); [A2A specification](https://a2a-protocol.org/latest/specification/)
- IETF: [draft-ietf-wimse-aims](https://datatracker.ietf.org/doc/draft-ietf-wimse-aims/);
  [draft-ietf-oauth-identity-assertion-authz-grant](https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/);
  [draft-niyikiza-oauth-attenuating-agent-tokens](https://datatracker.ietf.org/doc/draft-niyikiza-oauth-attenuating-agent-tokens/)

**New in this survey (§3.9).**
- [OBPE, arXiv:2608.27646](https://arxiv.org/abs/2608.27646) · [EBL-Core, arXiv:2609.11596](https://arxiv.org/abs/2609.11596)
- Zhu & Wang: [arXiv:2609.21284](https://arxiv.org/abs/2609.21284), [2610.00347](https://arxiv.org/abs/2610.00347),
  [2610.00349](https://arxiv.org/abs/2610.00349)
- [SAGA-BFT, arXiv:2605.12364](https://arxiv.org/abs/2605.12364) · [Mandate](https://github.com/pkravella/mandate) ·
  [AgentCity, arXiv:2604.07007](https://arxiv.org/abs/2604.07007) · [Jing, arXiv:2609.38224](https://arxiv.org/abs/2609.38224) ·
  [Will the Agent Recuse?, arXiv:2606.06460](https://arxiv.org/abs/2606.06460)

**Standards and guidance.**
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework); [Playbook](https://airc.nist.gov/airmf-resources/playbook/);
  [TACIP concept note](https://www.nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure)
- [AI Agent Standards Initiative](https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure);
  [NCCoE agent identity concept paper](https://csrc.nist.gov/pubs/other/2026/02/05/accelerating-the-adoption-of-software-and-ai-agent/ipd) and
  [summary of comments](https://pages.nist.gov/nccoe-ai-identity/summary-of-comments.html);
  [COSAiS](https://csrc.nist.gov/Projects/cosais); [IR 8596](https://csrc.nist.gov/pubs/ir/8596/iprd);
  [CAISI red-teaming insights](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [EU AI Act Service Desk: agents](https://ai-act-service-desk.ec.europa.eu/en/ai-act/faq/how-are-ai-agents-addressed-within-ai-act-0)
- [CSA Agentic AI IAM](https://cloudsecurityalliance.org/artifacts/agentic-ai-identity-and-access-management-a-new-approach);
  [CSA Agentic Trust Framework](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents)
- [CISA: Careful adoption of agentic AI services](https://www.cisa.gov/resources-tools/resources/careful-adoption-agentic-ai-services)
  (landing page; the PDF is at `doc/careful_adoption_of_agentic_ai_services.pdf`)
