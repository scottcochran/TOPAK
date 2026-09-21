<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: Theory of Operation checkpoint with ADR references session 09.11 (https://claude.ai/chat/8e4b4455-6594-4d23-a77a-eae3ac70ea8e), `create_file` turn 1, file `topak-theory-of-operation-2026.09.11.md`. No later edits.
>
> **Superseded** by 2026.09.12. §9 is the 09.11 proposed text of ADR-0001–0010; the Context/Decision/Consequences paragraphs for 0001, 0003, 0005, 0006, 0007, and 0009 match the tranche-1 records verbatim.
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

# TOPAK — Theory of Operation

**Checkpoint 2026.09.11** · supersedes 2026.09.10 · *The Gripping Hand*

Previous checkpoint: "TOPAK theory of operation checkpoint" (2026.09.10). This one records
the delta from ten design sessions since, the decisions that are now firm enough to write
down as Architecture Decision Records (ADRs), and the open list as it stands.

---

## 0. The six lines, restated

The 2026.09.10 checkpoint was organized around six structural claims. Four survive
unchanged. Two changed shape.

| 2026.09.10 | 2026.09.11 |
|---|---|
| Three TLA+ spec domains: CI, Orch, Agent | **Changed.** `Build(Contain) → Run(Contain)`. The third domain was never a peer; it is a membrane, and it now appears in two places. |
| All PC/EC with limited EL zones | **Amended.** Zone 3 (the effect stream) is redefined — Kafka is no longer the ordering authority. |
| CI is a directed acyclic graph (DAG) with its own TOPAK | Unchanged, and now structural rather than observational. |
| CI is an artifactory for Orch | Unchanged; promotion gates gain external backing. |
| Agent is a membrane inside Orch | Unchanged, and now has a published name and a theorem. |
| Principals are agent LTROs (Listener/Thinker/Reader/Observer) | Unchanged; gains a placement constraint. |

---

## 1. Domain structure: `Build(Contain) → Run(Contain)`

From the pattern-category assessment chat. The nesting is not decorative — in TLA+ terms it
is specification conjunction plus hiding: `Run`'s spec conjoins `Contain`'s, and `Contain`'s
internal variables are existentially quantified away at the `Run` level. That *is*
"contained spatially, excluded epistemically," written in notation instead of prose. The
parentheses are the refinement boundary.

It also reads as parameterization, which is the thesis: `Run` is parametric in what sits
inside the membrane. Any LTRO satisfying the action alphabet plugs in and `Run`'s safety
properties are unchanged. `Run` does not know what the agent is and does not need to.

Two things fall out:

- **The CI naming collision dissolves.** Renaming the domain `Build` kills the continuous
  integration / critical infrastructure ambiguity that was an open item on 09.10.
- **`Build` needs the parentheses too.** If the Byzantine threat lives in Build — agents
  authoring the rules they will later be judged by — then Build has contained agents and the
  membrane belongs there as well. This is what "CI is a DAG with its own TOPAK" already
  implied; the notation just makes it a structural argument instead of a footnote. The
  alternative is to claim Build's containment is genuinely different because its commit
  point is a human signing key rather than an emission — in which case the asymmetry is a
  claim being made, not an oversight. **Unratified. See ADR-0002.**

Caution carried forward: the notation does not survive speech, and it names *domains* while
TOPAK names *components*. Readers will try to merge the two axes and fail, since T appears in
all three domains and K spans all three. A small component × domain mapping table kills that
confusion outright. Still unwritten.

---

## 2. Consistency model

Unchanged from 09.10 except zone 3:

- **Build — PC/EC.** Unavailability costs a stalled pipeline. No leases, no liveness-under-partition requirement.
- **Run core (the epoch) — PC/EC.** Live bundle version, leadership, membership, admission.
- **EL zone 1 — enforcement (PA/EL).** Rego is a pure local function over a pinned bundle. Consistency by version pinning, not coordination.
- **EL zone 2 — leases (mixed).** Grant is a consensus decision; expiry is a local clock read. Expired lease is a safe state, so EL is sound by construction.
- **EL zone 3 — the effect stream. Redefined.** Kafka's requirement was already durability (acks=all) rather than consistency. As of the erasure decision it is also no longer the ordering authority: with a topic per principal per round, ordering within a partition no longer buys a global timeline. The causal frame lives in Paxos plus a vector clock. **This is a change to what the K means and must be stated in the article rather than discovered by a reader.**

Unifying rule, unchanged and still the sharpest sentence in the design: **consensus for
grants, local for denials.** A wrong denial costs availability; a wrong grant costs
containment.

Timing invariant, unchanged: **W < L < D** — propagation window ~1s, lease 10–30s, observer
detection lag ~30s. W covers propagation only and absorbs neither decision latency nor D.

---

## 3. The membrane, with external backing

From the Moon & Varshney analysis (*Containment Verification: AI Safety Guarantees
Independent of Alignment*, arXiv:2605.09045v2).

**What they give us for free:**

- The membrane is **havoc oracle semantics** — the agent modeled as a method with an empty
  body whose return ranges over the entire action type. "Model the agent the way you model
  the environment" was the same move without the name or the theorem.
- The completeness assumption is their **effect exclusivity**, and they place it in the
  trusted base rather than proving it. Citing them converts the weakest-looking assertion in
  TOPAK into a published, named one.
- The Byzantine-threat-lives-in-Build inversion is **empirically confirmed** by their §4.2
  pipeline failure: an agent recognized a schema mismatch and abstained, the template field
  went unwritten, the boundary predicate became vacuously true, and all three validation
  gates passed green. Spec-authoring agents silently narrowing the property is not
  hypothetical.
- Their G1/G2/G3 gates are directly importable as promotion gates.

**Where TOPAK differs, and why that is the contribution:**

- **Concurrency.** Their theorem is a single-process labeled transition system; they
  explicitly exclude concurrency, side channels, timing, and hardware. Theorem 3.2 does not
  lift to a distributed setting as written. Stale-bundle-under-partition, epoch fencing,
  split-brain — all of it lives where their theorem does not reach. This is the best
  differentiation claim available.
- **Property class.** Their Π is a transition predicate over one step. It cannot express
  liveness, eviction thrash, deadlock, or two principals jointly reaching a forbidden state
  over time. TLA+ can. Second real contribution.
- **Policy locus — a genuine disagreement.** Their boundary policy sits inside the verified
  artifact and inside the trusted base. TOPAK deliberately externalizes policy into signed
  Rego bundles that change at runtime without re-verification. See ADR-0010.
- **No sandbox layer.** They layer containment verification *over* process sandboxing. TOPAK
  asserts Kafka is the sole effectual channel and provides no mechanism that makes it so.
  Still open.

Position TOPAK as **containment verification lifted to a distributed, multi-principal,
policy-mutable setting.**

---

## 4. Typed action discipline — the fork, resolved

This was the 09.10 open item flagged as the collapse case under Theorem 3.2. It is now a
decision procedure rather than a gap, from the colocation chat.

The question "when may the action envelope be widened?" splits into two questions that should
not share a name:

- **Syntactic lift.** The field is structurally present in a constrained call interface —
  URL, path, amount, tool name, byte count. The harness extracts it mechanically, totally,
  without interpretation. Pure alphabet widening. Fine in any zone; cost is proof surface.
- **Semantic lift.** Deciding requires judging what the payload *means* — is this personally
  identifiable information, is this code hostile, is this output harmful. That needs a
  classifier, which is a model, which is unverifiable by the pattern's own premise. Putting
  it in the admit path puts a model in the trusted computing base.

**Rule: semantic judgment is never a lift.** It is an Observer finding, and findings may only
subtract authority, never add it. A classifier is safe as a trigger for deny, quarantine, or
eviction, and unsafe as a precondition for admit. This is the grants/denials asymmetry doing
the work again.

Second index is **reversibility**, orthogonal to the fault model: irreversible effect → deny
by default and let the guarded unit move from action to stage; reversible or staged → lift is
affordable.

Two corrections that came out of the same session:

- **The agent is Byzantine at every rung.** The CFT/PBFT ladder describes the *orchestrator*
  adversary — whether nodes or Observer replicas are hostile. The agent never gets a
  crash-fault model. Containment independent of alignment means it is a havoc oracle in
  audit-only shadow mode exactly as much as at PBFT+LTRO.
- **Adoption hazard.** In shadow mode, denying costs nothing visible, so teams lift lazily
  where nothing is being blocked, then promote up the ladder carrying an envelope that has
  already lost closure. The erosion happens at the rung where nobody is watching. Argues for
  totality checks on lifted fields as a Build gate — the direct countermeasure to the silent
  abstention failure.

---

## 5. Erasure versus replay — closed, with a residual

Flagged on 09.11 as the one gap untracked anywhere. Now has a mechanism.

**Root cause.** Ordinary systems never durably record data in use; that state is ephemeral by
construction, which is why erasure playbooks only discuss data at rest. TOPAK deliberately
moves data in use into data at rest — context windows, chain of thought, intermediate
reasoning, persisted at full fidelity, signed, forever. That single move is the entire gap.

**Five demand types the mechanism has to cover:** never write it; destroy it; mutate it;
withhold it from some readers while retaining it for others; hide that it ever existed. Types
4 and 5 are beyond crypto-shredding's reach, and type 5 defeats tombstones, since a tombstone
is itself a disclosure. Type 3 is the worst fit for an append-only signed log, because nothing
in the design contemplates a past event being *wrong* rather than merely sensitive.

**The resolution: topic per principal per epoch/round, sealed on emit completion.** The topic
becomes the unit of erasure, and that unit lines up with the unit policy is already pinned to.
Delete the topic, delete the round — no tombstones, no crypto-shredding, no signature problem,
because a whole sealed container is dropped rather than edited. It also gives masking failures
a remedy: if the wrapper misses a secret, the blast radius is one round-topic. Without it, a
miss is permanent.

**What it costs:** Kafka stops being the ordering authority (§2) and, combined with per-use-case
retention and archive-as-ETL, stops being the system of record.

**Residual, and it should be stated rather than left silent:** data in use. Once plaintext
enters an agent, an evaluator, or a replay harness, there is no control beyond trusting the
runtime. SCI-grade claims imply attestation and a trusted execution environment for the
*replay harness* specifically, since that is where old material re-enters use under new
conditions.

---

## 6. The cost model — "the safety tax is paid in tokens, not in consensus"

From the time-expenditure session. Control-plane cost per agent action:

| Component | Cost |
|---|---|
| Rego eval against a pinned bundle | 0.1–5 ms |
| Ed25519 sign/verify | microseconds |
| Kafka produce, acks=all, intra-AZ | 5–20 ms |
| One Paxos round | 1–2 ms intra-AZ, 10–60 ms cross-region |

Low tens of milliseconds worst case against a 5-second decode — a fraction of a percent, below
the noise floor of provider-side latency variance.

The real tax is cognitive. LTRO serializes four stages where a monolith had one, and the
Observer gates emission from quarantine, so it sits on the critical path even when its
replicas fire in parallel (pay max, plus the PBFT rounds). **Expect 2–4× wall clock per agent
action, essentially all of it additional decode.**

This is the opposite of what a skeptical reader expects, which makes it worth leading with.
And since every boundary event carries a durable timestamp on the effect stream, TOPAK is
self-instrumenting for exactly this budget — the latency argument is measurable from the audit
log rather than asserted.

---

## 7. Worked examples now in hand

**Aviation (767, Miami overrun).** Near-ideal because every failure point maps to a
declarative, observable predicate: O enforcing stabilized-approach criteria at the 1,000-foot
gate; T catching the emergent deceleration lockout chain (weight-on-wheels blocking both
reverse thrust and spoilers); P dissolving the authority gradient that let a captain override
a first officer's repeated warnings — Paxos as crew resource management with rank removed. The
limit is the valuable part: eviction is inapplicable once a crew has hands on the controls at
223 feet, which forces a binary between advisory mode (another ignored warning) and actuation
authority (MCAS-class risk). Resolution is break-glass, not prohibition. See ADR-0009.

**Scientific method.** Maps onto the *procedural* commitments of science — preregistration,
provenance, reproducibility, peer review, retraction — not its epistemics. Strongest mapping
is Build: the citation graph is already a DAG, the literature is already an artifactory, and
reproducibility is artifact pinning and nothing else. The revocation path that bypasses
promotion has no counterpart in real science — retracted papers keep getting cited because
there is only a notice, never a revocation channel. Where it breaks, and these are honest
limits: no ground-truth invariant (TLA+ invariants are stipulated, nature's are discovered),
default-deny is anti-serendipity, and the disposition toward counterexamples is inverted — in
TOPAK a counterexample is a defect, in science it is the product.

---

## 8. Publication plan

Order, by increasing difficulty, which runs **exactly opposite** to the dependency order:

1. **Agents** — the motivation piece. "← You are here." Autonomous agent deadlocking, going
   rogue, lying about what it did. Every failure mode named creates demand for a later
   article. Subtitle pays off through LTRO: *hold* is the Observer gating emission from
   quarantine (output exists but has not become an effect), *fold* is discarding the
   quarantine. The agent does not get a vote. Do not extend the lyric past hold/fold — walking
   away and running imply an exit option, which contradicts the membrane.
2. **Kafka** — partition-key design and ordering guarantees for replayable agent audit logs,
   not a generic explainer. Now also has to carry §5's redefinition.
3. **OPA**
4. **Paxos**
5. **TLA+** — arrives with Paxos as a concrete artifact the reader already understands.

Because difficulty inverts dependency, each article should **end with the debt it could not
discharge** ("nothing here proves the eviction rule terminates"), so the IOUs are explicit and
compounding rather than glossed, and TLA+ lands as the payoff that settles all of them.

Start the spec in parallel, not after article 4, scoped hard: *an evicted agent stops being
able to write to its topics, and eviction terminates.* Weekend-to-two-weeks, small enough to
fit in an article, real enough to model-check. Interstitial track (PACELC, zero trust, plane
separation, ADR meta-process) tagged visibly as separate, one per core article as a ratio held
to rather than "as needed."

Six things the introductory article must carry to be defensible: the thesis stated outright
(the cognitive layer is unverifiable in principle, so verify the cage, not the occupant); who
the Paxos participants are (orchestrator decisions *about* agents, not consensus *among*
agents); consensus for grants, local for denials; the plane split with the membrane named plus
the deployment ladder including the enforce-without-consensus rung; an explicit scope boundary
on "Safe by Design" (verified orchestration says nothing about output safety); and the Moon &
Varshney citation for effect exclusivity.

---

## 9. Architecture Decision Records

Numbering is provisional — renumber against the real ADR log. Status reflects what has
actually been ratified versus what is a standing proposal from a design session.

---

### ADR-0001 — Rename the CI domain to `Build`; adopt `Build → Run(Contain)` notation
**Status:** Proposed (2026.09.11)

**Context.** The domain named CI collided with critical infrastructure in an article that
discusses both. Separately, the 09.10 checkpoint listed three peer spec domains while the
boundaries session had already established that Agent is contained spatially and excluded
epistemically — a refinement boundary, not a peer.

**Decision.** Rename the domain `Build`. Express domain structure as `Build → Run(Contain)`,
where the arrow is authority flow and the parentheses are the refinement boundary
(specification conjunction plus existential hiding of internal variables).

**Consequences.** Kills the naming collision. Makes the containment claim structural rather
than rhetorical, and makes `Run` visibly parametric in its agent. Gives the diagram its spine
and probably its caption. Does not survive being spoken aloud, so prose must carry the nesting
independently. Introduces a second axis (domains) alongside components — requires a mapping
table or readers will conflate them.

---

### ADR-0002 — Apply the membrane in `Build` as well: `Build(Contain) → Run(Contain)`
**Status:** Proposed (2026.09.11) — **decision required**

**Context.** The published inversion is that the Byzantine threat lives in Build, where agents
author the envelope they will later be judged against. Build therefore has contained agents.
Moon & Varshney §4.2 provides the empirical failure: silent abstention, vacuously true
predicate, green gates.

**Decision (pending).** Either apply `Contain` at both domains, making it a reusable component
rather than a third domain and making the Build recursion structural; or assert that Build's
containment differs because its commit point is a human signing key rather than an emission,
and the regress terminates at a declared axiom set.

**Consequences.** Option 1 unifies the pattern and strengthens the recursion claim already made
("Build is a DAG with its own TOPAK"), at the cost of a larger proof surface and a harder
story about who signs. Option 2 is defensible but must be stated as a claim; left implicit it
reads as an oversight. Silence is the only wrong answer.

---

### ADR-0003 — Topic per principal per round, sealed on emit, as the unit of erasure
**Status:** Accepted (2026.09.11)

**Context.** Erasure obligations require that specific content be destroyed, per subject, at
arbitrary times, provably. Replay requires that nothing ever be removed. Retention expiry
deletes by age rather than by subject; tombstones break gapless ordering and are themselves
disclosures; crypto-shredding leaves a verifying envelope over unreadable ciphertext — a hole
no auditor can distinguish from suppression.

**Decision.** One Kafka topic per principal per epoch/consensus round, locked on emit
completion. Access by ACL. Retention scoped per use case. Separate read-only principals for
audit. Replay explicitly authorized or refused. Masking and suppression enforced by wrapper
Rego at write time. No tiered storage. Archive is its own ETL per use case.

**Consequences.** The topic becomes the unit of erasure and lines up with the unit policy is
pinned to. Deletion is dropping a sealed container, so signatures and hash chains are never
edited. A masking miss is now recoverable with a blast radius of one round. Forces ADR-0005.
Topic count scales with principals × rounds — broker metadata pressure is a real operational
cost and needs a lifecycle story.

---

### ADR-0004 — Separate control-plane facts from cognitive payloads
**Status:** Proposed (2026.09.11)

**Context.** Trace conformance against the TLA+ specification operates over the abstract state
machine — actions, identities, transitions, causal ordering. It does not need prompt text.
Forensics needs the text. Two consumers, two retention appetites, one store.

**Decision.** Log the hash and a pointer for cognitive payloads; keep plaintext in a separately
governed store built for deletion.

**Consequences.** The log keeps everything replay and conformance genuinely require, and the
material carrying the legal exposure sits somewhere designed to be destroyed. Partially
redundant with ADR-0003 for the live path; still load-bearing for the archive, where round
topics no longer exist. Adds a join to every forensic query.

---

### ADR-0005 — Kafka is neither the ordering authority nor the system of record
**Status:** Consequential — forced by ADR-0003; ratify or revisit ADR-0003

**Context.** With one topic per round, within-partition ordering no longer yields a global
timeline. With per-use-case retention and archive-as-ETL, the log is not durable in the sense
"system of record" implies.

**Decision.** The causal frame lives in Paxos plus a vector clock. The archive is the system of
record. Kafka's guarantee is durability in the window (acks=all), not ordering across the
system.

**Consequences.** Changes what the K in TOPAK means and must be stated explicitly in the
component article rather than discovered by a reader. Requires a vector clock design that does
not yet exist. Trace conformance must be shown to work against reconstructed rather than
native ordering.

---

### ADR-0006 — Erasure is a privileged, modeled, consensus-ordered event
**Status:** Proposed (2026.09.11)

**Context.** In a fail-closed zero-trust design, deletion cannot be an out-of-band operator
action, because that is exactly the capability to rewrite history. The erasure path is
simultaneously a legal requirement and the highest-value attack surface in the system — it is
how a rogue agent or hostile insider covers tracks.

**Decision.** Erasure is an event: ordered by consensus, authorized by Rego, modeled in TLA+,
and recorded in the log it modifies.

**Consequences.** Erasure inherits the full control-plane cost and latency, which is fine — it
is not on the hot path. Requires a safety property distinguishing lawful erasure from
history rewriting, which is a genuinely interesting spec obligation and a good article. Does
not address demand type 5 (hide that it existed), where recording the erasure is itself the
disclosure. That remains open.

---

### ADR-0007 — Semantic judgment is never a lift
**Status:** Proposed (2026.09.11)

**Context.** Widening the typed action envelope is sometimes necessary and sometimes fatal. The
distinguishing axis is not the fault model or the deployment rung — the agent is Byzantine at
every rung — but whether admitting the field requires interpreting what the payload means.

**Decision.** Syntactic lift (mechanical, total extraction from a constrained call interface)
is permitted in any zone. Semantic lift is prohibited in the admit path. Classifier output
enters as an Observer finding, and findings may only subtract authority, never add it.

**Consequences.** Keeps models out of the trusted computing base, which is the pattern's own
premise. A classifier is usable as a trigger for deny, quarantine, or eviction. Some genuinely
desirable policies become unexpressible at admit time and must be restated as detections.
Requires totality checks on lifted fields as a Build gate to prevent shadow-mode envelope
erosion.

---

### ADR-0008 — Observer replicas are not colocated with the Thinker
**Status:** Proposed (2026.09.11)

**Context.** Colocating for logit access is tempting for bandwidth. The Reader is the role that
needs logits, and it is already inside the membrane and was never an independent fault domain.

**Decision.** Reader may colocate with Thinker. Observer replicas may not colocate with a
Thinker, and no two Observer replicas may share a device.

**Consequences.** Shared device means shared driver, VBIOS, ECC domain, thermal and power
event, and host kernel — correlated failure takes out watcher and watched together, and a
Byzantine quorum with co-resident replicas is arithmetic fiction. Shared device memory and
CUDA IPC handles are an unmodeled effect path, which is the effect-exclusivity collapse case
and worse than at the Kafka boundary because no spec variable exists for it. Contention becomes
an availability attack against fail-safe-by-absence. Colocating the Observer would also
re-scope it to per-agent, undoing the hoist to a shared orchestrator-level replicated group and
collapsing ~9 model instances / 6 spec processes back toward 40. Cost of the decision is
hardware and inter-node latency.

---

### ADR-0009 — Break-glass is a modeled, quorum-witnessed path, not a prohibition
**Status:** Proposed (2026.09.11)

**Context.** The aviation worked example exposes the limit of eviction as the sole enforcement
primitive: at 223 feet with hands on the controls, there is nothing to evict. Advisory-only
becomes another ignored warning; actuation authority replicates MCAS-class risk.

**Decision.** Provide an explicit override path that is logged, quorum-witnessed, and modeled —
living on the control/data plane split rather than being forbidden.

**Consequences.** Converts detection into a committed decision no single actor can unilaterally
override, which is the strongest thesis statement available for a general audience. Requires
TLA+ properties that permit override without the override becoming a general bypass — a hard
and worthwhile spec problem. Must never be used to justify data-plane autonomy in irreversible
domains.

---

### ADR-0010 — The verified object is the enforcement mechanism and its epoch discipline; the bundle is a versioned parameter
**Status:** Proposed (2026.09.11)

**Context.** Moon & Varshney place boundary policy inside the verified artifact and inside the
trusted base. TOPAK externalizes policy into signed Rego bundles that change at runtime without
re-verification. This is a real disagreement, not a detail.

**Decision.** State plainly that what is verified is the enforcement mechanism, its version
pinning, and its epoch fencing — with the policy bundle as a versioned parameter — and that
proof coverage is being traded for operational agility.

**Consequences.** Honest, and pre-empts a reviewer making the point first. Puts weight on Build
gates, since bundle correctness is now assured by promotion rather than by proof. Pairs with
the pre-blessed default-deny bundle, staged and resident: instantiate rather than fetch.

---

## 10. Open list

**Closed since 09.10**

- ~~Audit-log erasure versus replay~~ — ADR-0003 through ADR-0006, residual noted below.
- ~~CI naming collision~~ — ADR-0001.
- ~~Does the membrane get a name?~~ — yes: `Contain`, named by the notation.
- ~~Typed action discipline as an open fork~~ — ADR-0007. The discipline now has a decision
  procedure; the alphabet itself is still unwritten, which is a work item rather than an
  unknown.

**Still open from 09.10**

- **Signed-message format.** Narrowed but not settled: envelope/payload split either way,
  signing received bytes in place rather than re-serializing, and ADR-0003 makes sealed-topic
  deletion rather than ciphertext-shredding the erasure mechanism — which weakens the case for
  canonical CBOR over protobuf with canonical JSON mapping.
- **The diagram.** Now has a spine (`Build(Contain) → Run(Contain)`) and a required content
  (the 1→2→3 assumption chain). Still not drawn.
- **Component × domain mapping table.** Needed to stop readers merging the two axes.

**New**

- Vector clock and causal-frame design, now that Kafka is not the ordering authority (ADR-0005).
- Trace conformance against archived, reconstructed ordering rather than native log ordering.
- Replay-harness attestation / trusted execution environment — the data-in-use residual.
- Demand type 5 (hide that a record existed) versus a recorded erasure event (ADR-0006).
- No sandbox layer beneath the membrane; Kafka-as-sole-channel is asserted, not enforced.
- Round-topic lifecycle and broker metadata pressure at scale (ADR-0003).
- Totality checks on lifted fields as a Build gate (ADR-0007), countering shadow-mode erosion.
- Break-glass safety properties that permit override without becoming bypass (ADR-0009).
