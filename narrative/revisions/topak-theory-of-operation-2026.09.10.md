<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: TOPAK theory of operation checkpoint session 09.10 (https://claude.ai/chat/382e85af-e7f4-4ebf-ba54-1d993e6a2c7a), turn 1, inline response (no file). No later edits. The response's one-line lead-in ("Here's the checkpoint, filled in from the design threads.") is omitted; everything after it is verbatim. File name assigned at recovery.
>
> **Prompt it answers** (turn 0, Scott, verbatim): *3 TLA spec domains: CI, Orch, Agent · All PC/EC with limited EL zones · CI is a DAG with its own TOPAK. · CI is an artifactory for Orch · Agent is a membrane inside Orch · Principals are agent LTROs.* The body calls these "your six lines."
>
> **Superseded** by 2026.09.11. Uses pre-rename vocabulary (CI, Orch).
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

## 1. Three spec domains — with one caveat

The cutting criterion was "does this domain have its own notion of *a step*": artifact promotion (CI), deployment epoch (Orch), agent action (Agent). That still holds. But line 1 and line 5 are in tension, and you resolved it in the boundaries thread: Agent is contained *spatially* and excluded *epistemically*. So it's a refinement boundary, not a peer. Either it's two domains plus a membrane, or three where the third is deliberately spec-light — it can't be a sibling of Orch.

What the Agent domain must contain even when spec-light: the **action alphabet** and the **completeness assumption** ("all agent effects are observable on Kafka"). Every safety property in CI and Orch is conditional on it, and it isn't provable in-model because it's a claim about what the model omits. Dependency chain: 1 → 2 → 3 as assumption chains, 3 → 2 as trace evidence.

## 2. PC/EC with limited EL zones

- **CI — PC/EC, no tension.** Unavailability costs a stalled pipeline, nothing more. No leases, no timeouts, no liveness-under-partition requirement.
- **Orch core (the epoch) — PC/EC.** Live bundle version, leadership, membership reconfiguration, admission. Split-brain here means two policy versions enforcing at once.
- **EL zone 1 — enforcement (PA/EL).** Rego is a pure local function over a pinned bundle. Consistency comes from version pinning, not coordination.
- **EL zone 2 — leases (mixed).** Grant is a consensus decision; expiry is a local clock read. Expired lease is a safe state, so EL is sound by construction.
- **EL zone 3 — the effect stream.** Careful with framing: if Kafka is the sole effectual channel it isn't observability, and its requirement is durability (acks=all), which is a different axis than consistency.

Unifying rule: **consensus for grants, local for denials.** Denial is monotone and fail-safe. Eviction looks bimodal but isn't — anyone slams the door (EL), the quorum records that it's locked (PC).

Sharp edge: stale-bundle-under-partition. Stale is safe if the new bundle loosened, unsafe if it tightened. Epoch fencing bounds it — bundle older than the live epoch by more than W, agent fences. Gives you a publishable number: max policy propagation delay. Real exposure is **W + D** (prevention window + detection lag) for anything the observer catches rather than the sidecar.

## 3. CI is a DAG with its own TOPAK

DAG per release: steps 3–9 fan out from the TLA+ spec, fan back in at the bundle; step 11 closes a cycle across releases. The property is **coherent cut** — every branch traces to the same root revision. Fan-in failure (Rego from ADR rev 7, schemas from rev 6) is the interesting bug, and nothing about linear ordering catches it.

Lineage is the only state that matters; bytes are incidental. CI is the only boundary that *produces* attestation, which is what makes reproducibility a CI-only requirement. Monotone except revocation — spec revocation first.

Inner TOPAK:
- **T** — spec of promotion; a step is "artifact advances a tier."
- **O** — Rego over promotion requests: signatures present, provenance well-formed, inputs pinned. Pipeline code asks, doesn't decide.
- **P** — blessing is a quorum decision, not one build server's assertion.
- **A** — derivation agents and human reviewers, same policy.
- **K** — the promotion log; the lineage DAG is a projection of it.

Tail-eating is Trusting Trust. Two exits: stratify (CI-0 human-attested, blesses CI-1 — names your TCB) or diverse double compilation (agreement on the hash *is* the attestation, quorum members are independent implementations). Regress terminates at a declared axiom set: human signing keys plus a root ADR. **The inversion worth publishing: the Byzantine threat lives in CI, not at runtime.** Runtime agents violate rules; CI agents author the rules they'll be judged by.

## 4. CI is an artifactory for Orch

The signed bundle is the *entire* contract across the seam. CD sits on the Orch side, not CI — it transforms CI's terminal state (signed artifact) into Orch's input (deployed configuration), which makes the seam an explicit contract rather than a handoff.

Two things that must bypass the normal promotion path: **revocation** (must reach the epoch directly, or your propagation number is honest and your exposure isn't) and the **pre-blessed default-deny bundle** (staged and resident, so e-stop activation is instantiate, not fetch).

## 5. Agent is a membrane inside Orch

Containment is true in deployment topology and false in the formalism — you model an agent the way you model the environment, unbounded nondeterminism. That's what "untrusted" cashes out to.

Consensus grouping does *not* follow from the spec merge. Still separate groups, on churn and rate: agent membership reconfigures constantly with short high-volume leases; deployment epochs change rarely and must never be wrong. And the merge risk to watch — **agents are the only Byzantine actors at runtime.** Orchestration nodes crash; agents scheme. If the agent boundary stops being a section heading it's easy for the spec to quietly acquire an assumption of agent good behavior.

## 6. Principals are agent LTROs

**Principal** is the unit of identity: what holds the lease and gets evicted. The same Rego binds a human principal and an LTRO principal, so the spec needs no separate case. LTRO = Listener / Thinker / Reader / Observer — three deterministic stages wrapping one nondeterministic agent.

- Intra-agent stages stay a sequential deterministic pipeline: durable log, no ballots, phases in the spec.
- **Emission is the commit point** — the only place an effect becomes irrevocable, and the only place unanimity is required. Everything before it is recoverable by discarding a quarantined topic.
- The Observer's vote is not the model's verdict: the Observer emits a typed finding, the wrapper's Rego turns it into a vote. The commit participant is deterministic policy code, which is what makes it specifiable.
- Human peer status is scoped: peer at identity, authorization, audit. Not a peer under the completeness assumption — a human can pick up a phone. Safety properties quantify over *contained* principals only.

## Also in the checkpoint but not in your six lines

**Deployment ladder,** each rung defined by the adversary it survives: audit-only (shadow mode — Rego evaluated, decisions logged, nothing blocked), CFT, CFT+LTRO (guarded unit moves from action to stage), PBFT+LTRO (adversary is the wrapper or an observer replica; only pays under genuinely independent failure). Named gap: the **enforce-without-consensus** rung — single orchestrator, OPA blocking, Kafka log, no Paxos. That's most real adopters.

**E-stop symmetry: CI stop = no new authority, Orch stop = no exercise of authority.** Both must fail safe by *absence* — deadman heartbeat is the guarantee, default-deny publish is only the accelerant. Halt ≠ purge. Reset voids leases and never resumes. Effectors validate epoch at consume time.

## Open, as of this checkpoint

- Does the membrane get a name in the article, or stay implicit in the plane split?
- Typed action discipline at the agent boundary — still unstated, and it's the collapse case under Moon & Varshney Thm 3.2.
- Signed-message format: protobuf + canonical proto3 JSON for Rego, versus canonical CBOR once you're signing. Envelope/payload split either way.
- The diagram. Still "insert pretty diagram here" — and the 1→2→3 assumption chain is what it should show.
- The CI collision: continuous integration vs critical infrastructure, same article.
