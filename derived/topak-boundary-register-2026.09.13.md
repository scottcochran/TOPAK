<!-- RECOVERED · FOLDED · 2026-09-15 · tranche 2 -->
> **Recovery note.** Source: Boundary register session 09.13 (https://claude.ai/chat/dc8a8875-0eb9-4494-94b6-aa14802085e1), `create_file` turn 5, file `topak-boundary-register-2026.09.13.md`. No later edits; the 09.13 assessment session (ee1a0c06) read it without changing it.
>
> Text below is verbatim from session history (HTML entities normalized). Nothing was drafted against this
> document, so cleanup step 3 (2026.09.15) changed only this header.

# TOPAK — Boundary Register

**2026.09.13** · companion to the Theory of Operation checkpoint 2026.09.12 · *The Gripping Hand*

The open list has carried "the diagram" and "the component × domain mapping table" since
2026.09.11. This is the third thing both of those were circling: a register that states, for
every boundary in the design, **what crosses it, how often each side moves, at what instant the
crossing is checked, during what interval the boundary is untrue, and what happens when the
check is unavailable.**

The organizing correction this document makes: **temporal is not one boundary. It is an axis
that crosses every boundary.** The 09.12 checkpoint has epoch fencing and lease expiry filed as
a consistency concern, which hides the fact that bundle promotion, Persona evolution, and
e-stops are three structurally different temporal objects. They are not.

Nothing here is a ratified decision. Rows marked **†** are analysis from the 09.13 boundary
pass and are not backed by an Architecture Decision Record (ADR).

---

## 0. How to read the grid

Every boundary has three temporal properties, and they are independent:

- **Cadence** — the rate at which the artifacts on each side change. A mismatch between two
  cadences is what forces a boundary to exist at all.
- **Instant** — the moment at which two independently-evolving artifacts are pinned against
  each other and a check becomes decidable. A boundary with no instant has no enforcement point.
- **Interval** — the window during which the boundary's claim is untrue, or not yet known to be
  true. A boundary with an unbounded interval and no monotonicity argument is an open hole.

The fourth column is the question that has been the most productive one in this project:
**what happens if the human never shows up** — generalized to *what happens if the check cannot
run*. Fail-closed answers are cheap. Fail-open and undefined answers are the findings.

---

## 1. The register

| Boundary | Cadence (outer / inner) | Instant | Interval of untruth | If the check is unavailable |
|---|---|---|---|---|
| **B1 Domain** `Build \| Run` | Release / incident | **Promotion** — signature over provenance | None claimed; `Submit` is sole egress | Fail-closed. Pipeline stalls; PC/EC makes this affordable (ADR-0002) |
| **B2 Membrane** `Contain` | Release / per-action | **Admit decision** | None; rejection is synchronous | Fail-closed. Resident default-deny floor, no fetch dependency (ADR-0012) |
| **B3 Typed effect** | Release (validator) / Persona (decoder) | **Validate** — total over floor alphabet | None for admissibility; **unbounded for fidelity †** | Fail-closed. Parse failure is a local deny, monotone (ADR-0018) |
| **B4 Verified / parameterized** | Release / deploy / incident | **Promotion** — `bundle ⊑ floor` | Bundle staleness, **unbounded but floor-bounded below** | Fail-closed and *safe while stalled*. The model case (ADR-0010) |
| **B5 Plane** control-plane / cognitive | Release / per-emission | **Fact construction** at Observer finding | None claimed | Fail-closed; no payload crosses by default (ADR-0004) |
| **B6 Principal type** `Contained` / `Mediated` | Per-principal, static | **Lease grant** | Whole lease, for `Mediated` | N/A — predicate, not a runtime check (09.12 §5) |
| **B7 Seat** LTRO separation of duties | Release / Persona | **Seat binding** in Persona | None claimed | Fail-closed if binding is verified; **unstated †** (ADR-0016) |
| **B8 Persona / occupant identity** | Provider (**uncontrolled**) / Persona promotion | **Persona promotion only** | **Unbounded — no expiry, no re-attestation †** | **Undefined.** Largest empty cell in the grid (§8) |
| **B9 Retention / erasure** | Deploy / per-round | **Seal** on emit completion | Between emit and seal | Fail-closed on replay; **fail-open on forensics †** (ADR-0003, 0006, 0020) |
| **B10 Human authority** HITL / HOTL / HOOTL | Constitutive / supervisory / absent | **Gate** (HITL) or **non-refresh** (passive e-stop) | `D` — **unbudgeted †** | Build: stalls. Run: **proceeds** — HOTL is disabling only (09.12 §4) |
| **B11 Deployment rung** archetype / profile | Release / per-deployment | **Rung manifest** | None claimed | Fail-closed by subtraction; monotone (open — axis question) |
| **B12 Deployment stack** sandbox and below | — | **None — no mechanism exists** | **Permanent** | **Undefined.** Effect exclusivity is assumed, not enforced (§10.1) |
| **B13 Epoch / lease** temporal fence | Deploy / per-round | **Fence** / **expiry** | ≤ TTL for passive stop | Fail-closed. Expiry is a local clock read — **but see §9.1 †** |
| **B14 Gate approver** | — | **None — outside every theorem** | **Permanent** | **Undefined.** Approver is not evictable, therefore unmodeled (§10.2) |

---

## 2. The empty cells are the finding

Read the grid by its holes rather than its contents. Four rows have a missing or undefined
cell, and they are not equally serious.

| Row | Missing | Consequence |
|---|---|---|
| **B8 Persona** | No instant for provider-side change; no interval bound | Silent substitution breaks the pin with **no event anywhere in the system** |
| **B12 Sandbox** | No instant, no mechanism, permanent interval | Every containment theorem is conditional on an undischarged assumption |
| **B14 Gate approver** | No instant, no mechanism, permanent interval | The one authority in the design that no theorem constrains |
| **B10 Human** | Interval `D` named but never budgeted | HOTL without a response budget reproduces the ignored-warning failure |

**B12 and B14 are structural and known.** They are already on the open list and already have
honest treatment in the checkpoint. B8 is new as of the 09.12 Persona session and is not on the
open list at all.

**B8 is the one to act on.** It is the only row in the register where an artifact on the outer
side changes at a cadence TOPAK does not control, does not observe by default, and cannot fence.
Every other uncontrolled-outer-cadence row has an instant that catches it.

---

## 3. Cadence firewalls

The verified/parameterized boundary (B4) is a temporal boundary wearing spatial clothes. It
exists because of a rate mismatch, not because of a location, and the same argument now appears
at four layers:

| Artifact | Cadence | Crossing event | Verified |
|---|---|---|---|
| Mechanism (`Contain`, validator) | Release | Signed release | **Yes**, once |
| Minimal policy floor | Deploy — consensus-ordered | Floor change (ADR-0014, open) | **Yes**, with mechanism |
| Persona (+ decoder) | Persona promotion | Persona promotion | No — parameter |
| Operational bundle | Incident | Promotion, `⊑ floor` | No — parameter |
| Deployment rung | Per-deployment | Rung manifest | No — subtraction |

Each horizontal line prevents a fast-changing artifact from forcing re-verification of a
slow-changing one. That is the whole content of "verified invariant plus versioned parameter."

**Recommendation for the article.** It is currently presented three times — policy (ADR-0010),
syntax (ADR-0018), deployment (rungs) — as three separate structural moves. It is one temporal
argument applied three times, and it lands harder stated once.

**Bearing on ADR-0014.** "Floor authorship and change control" is a cadence question in
disguise: who may move an artifact from the incident row to the deploy row. That is the only
direction of movement that costs anything, and it is where the human signing key and the
vacuity gates concentrate.

---

## 4. Instants

The four instants in the design, and what each one buys.

**Promotion.** `bundle ⊑ floor` is decidable *because both artifacts are fixed at that instant*.
ADR-0018's obligation that the decoder targets the floor's alphabet has the same structure —
checkable at promotion, undecidable at any other time. Promotion is the only instant where two
different cadences meet, which is why every gate in the design has accreted there and why
Build's gate inventory is growing faster than it is being ratified.

**Seal.** ADR-0003: the round topic seals on emit completion. This is the instant a record
becomes immutable and the erasure unit becomes well-defined. The proposed Build unit is one
pipeline invocation instead — the genuine Build/Run divergence is the retention horizon, not the
granularity.

**Fence.** Epoch increment. Afterwards, actions carrying the prior epoch are rejected by
*mechanism* rather than by policy. The only place in the design where a temporal condition is
enforced without a policy lookup, which makes it the cheapest check in the system.

**Revoke.** Persona or lease revocation. **Semantics undefined** — see §8.

---

## 5. Intervals

| Interval | Bound | Status |
|---|---|---|
| `W` — effect propagation | ~1s | Stated |
| `L` — Observer detection latency | — | **Unmeasured**; the safety argument invokes it |
| `D` — human response budget | — | Named 09.12, never budgeted |
| Lease TTL | Configured | Stated; doubles as passive e-stop latency |
| Bundle staleness | Unbounded | **Safe by construction** — floor-bounded below (EL zone 1) |
| Retention horizon | Differs Build / Run | The genuine Build/Run divergence |
| Active e-stop latency | — | **Unbounded** (§7) |
| Break-glass grant | — | **No expiry** (§7) |
| Persona validity | — | **No expiry, no re-attestation** (§8) |
| Floor rollout | — | Not modeled (§9.2) |

**Bundle staleness is the model case and the only row that has solved its problem.** It is an
interval of incorrectness made harmless by monotonicity rather than by bounding. Nothing else in
the table has that property, and `L` structurally cannot acquire it, because detection is the
thing being delayed.

**Reason from that row.** For each remaining interval, ask whether a monotonicity argument is
available before reaching for a bound. Break-glass expiry (§7) is one where it is.

---

## 6. Structural companion — what crosses

Retained from the 09.13 boundary pass so the register stands alone.

| Boundary | Inside / above | Outside / below | What legitimately crosses | ADR |
|---|---|---|---|---|
| B1 | `Build` | `Run` | One signed, promoted artifact | 0001, 0002 |
| B2 | Principals (evictable) | Gate approvers (not evictable) | Typed actions in; admit/deny out | 0002 |
| B3 | Cognition | External state | `{tool invocation, principal emission}` | 0007, 0015, 0018 |
| B4 | Mechanism + pinning + fencing + floor | Bundles, Personas, rungs | Refinements only — subtraction | 0010, 0012 |
| B5 | Control-plane facts | Cognitive payloads | Facts cross; payloads do not | 0004 |
| B6 | `Contained(p)` | `Mediated(p)` | Safety theorems quantify inside only | 09.12 §5 |
| B7 | Listener / Thinker / Reader / Observer | — | Seat-scoped alphabet subsets (open) | 0008, 0016 |
| B8 | Pinned Persona | Provider-side model | Promotion only | 0016, 0017 |

**The criterion for B2 is evictability, not location** — if you can be evicted you are a
principal; if you are the authority that evicts you are at the gate. That is the sharpest
definition in the design and it is also exactly why B14 exists.

**The orientation rule.** Every boundary above is asymmetric in the same direction: crossing
toward more authority requires consensus, crossing toward less is local and monotone. Decision
layer (grants versus denials), policy layer (subtraction from the floor), syntax layer (parse
failure is a deny), deployment layer (rung subtraction), semantic layer (findings may deny,
never admit). This is not a boundary — it is the orientation of all of them, and it is stated
five times in five vocabularies across the current corpus.

---

## 7. E-stop taxonomy

| Kind | Trigger | Authority direction | Latency | Requires availability |
|---|---|---|---|---|
| **Passive** | Lease non-refresh | Subtracts | ≤ remaining TTL | **No** |
| **Active** | Unilateral human stop | Subtracts | Decision + `W` | Yes |
| **Break-glass** | Quorum | **Adds** | Consensus round | Yes |

Three gaps.

**7.1 Active e-stop latency is unbounded.** Passive has a clean bound — TTL, local clock read,
no authority required, works under partition. Active does not, because it depends on propagation
and on nothing being in flight. This is the number a regulator asks for before any other, and
the design does not have it.

**7.2 In-flight effects are undefined.** Stop-admitting is not stop-effecting. A tool invocation
already admitted and handed to an executor is outside the stop. ADR-0007's reversibility index
is adjacent but governs *guarded unit size*, not the drain interval. There is no quiesce
semantics anywhere in the corpus.

**7.3 Break-glass has no TTL, and this breaks the monotone story permanently.** Every other
authority movement in TOPAK is subtractive or self-healing. Break-glass *adds* authority, and
nothing in ADR-0009 makes the grant expire. A non-expiring grant is a permanent floor exception
acquired at incident cadence — precisely the accretion ADR-0013 exists to bound, arriving by a
route ADR-0013 does not currently cover.

**The fix is free.** Time-box the grant and let it expire by the same passive mechanism as a
lease. It reuses ratified machinery, requires no new component, and restores the monotonicity
claim across the whole authority surface.

**This also puts a temporal dimension on ADR-0013's non-composition obligation.**
*Erase-then-break-glass* and *break-glass-then-erase* are different failures, and the interval
between them is part of the property. The current statement of non-composition is untimed.

---

## 8. Persona evolution — the largest empty cell

ADR-0016 binds model, provenance, cryptographic identity, system prompt, decoding parameters,
decoder, and seat. All of that is a **pin**. The record says nothing about what happens when the
pinned thing moves, and the pinned thing is on the far side of a cadence TOPAK does not control.

- **Immutability is unstated.** Presumably any change yields a new Persona. If the record does
  not say so, the identity claim carries no weight.
- **Silent substitution is a change with no event.** A provider updates weights, rotates a
  tokenizer, or deprecates an endpoint. No promotion occurs, no epoch fences, no gate fires, no
  Observer finding is generated. The pin breaks without an instant. ADR-0019's decode
  observability is the only detector and it is optional, rung-gated, and explicitly barred from
  carrying Observer-latency claims. **This is the model-provider boundary appearing as a
  temporal hole rather than a trust one, which is the stronger framing for the article.**
- **No staleness argument exists for Personas.** A stale bundle is safe because the floor bounds
  it below. A stale Persona has no equivalent — nothing makes an out-of-date Persona
  monotonically less dangerous. Readers will assume the floor argument generalizes. State
  explicitly that it does not.
- **Revocation mid-round is undefined.** Does it fence the epoch, kill the lease, or seal the
  topic early? Each answer interacts differently with ADR-0003's seal-on-emit-completion.
- **No Persona expiry.** A mandatory re-attestation interval is the cheap version of the
  substitution problem and does not require decode observability to be enabled.
- **Interaction with ADR-0017's two-lineage archetype.** Whether two Personas from the same
  lineage at different versions count as independent for monoculture purposes is undefined. The
  answer determines whether a routine version bump silently collapses the archetype's
  independence claim — a safety property degrading with no event, which is the same failure
  shape as silent substitution one level up.

**Recommendation.** This is an amendment to ADR-0016 or a companion record, not an open-list
line. Minimum content: immutability by construction, an expiry or re-attestation interval,
revocation semantics against the seal, and a lineage-version independence criterion (which
ADR-0017 already owes a decidable version of).

---

## 9. Temporal vocabulary the corpus lacks

**9.1 Clock model.** The entire lease argument rests on "expiry is a local clock read." No clock
assumption is stated anywhere in the corpus — bounded drift, monotonic versus wall-clock, NTP
step behavior, what a backwards jump does to a fenced epoch. A lease-based safety argument with
no clock model is the standard hole in this class of design, and TOPAK currently has it. Cheap
to close, embarrassing to be caught on.

**9.2 Floor rollout semantics.** A floor change is consensus-ordered, but during rollout two
floors are live. Tightening and relaxing have different safety characters during that interval.
Probably fine under monotonicity — but that is a proof obligation, not an assumption, and no
record owns it.

**9.3 Epoch allocation.** Who issues epochs, monotonicity under partition, exhaustion behavior.

**9.4 Cold-start interval.** ADR-0012 handles cold start by residency, but the interval between
process start and floor-verified-resident is not characterized.

**9.5 Ordering after ADR-0005.** Kafka is neither ordering authority nor system of record.
Paxos orders admit decisions. Cross-principal causality remains the open vector-clock and
causal-frame item, contingent on the Observer quarantine gate question — still the cheapest open
question on the board, and it now blocks two things rather than one.

---

## 10. Boundary categories absent entirely

**10.1 Sandbox and below.** Moon & Varshney Figure 1: model → containment layer (formally
verified) → sandbox → host kernel → hardware (operationally audited). TOPAK has the containment
layer and nothing beneath it. The proposed Build action-alphabet record states the confinement
obligation in §6 and explicitly does not discharge it. Consequence, stated plainly: **effect
exclusivity is an assumption, not a mechanism**, and every containment theorem should be written
conditional on it. Use the paper's own stack vocabulary — it converts a TOPAK-specific weakness
into a named layer TOPAK declines to own, which is both honest and stronger.

**10.2 The gate approver.** Outside `Contain`, outside every theorem, unmodeled. The Build
Observer proposal makes the *basis* of an approval an audited object but does not make the
approver `Contained` and should not be written as if it does. No record owns the residual. This
is also the NIST GOVERN-shaped hole.

**10.3 Toolchain and supply chain.** The trusting-trust regress terminates at a declared axiom
set plus one verified artifact — but the verifier binaries, the Rego compiler, the model
checker, and the compiled-output path are never itemized as a boundary with its own crossing
rule and its own cadence.

**10.4 Tenancy and blast radius.** Nothing separates principals belonging to different tenants
or workloads. The archetype is SCI/HIPAA-rigorous, which makes the absence conspicuous.

**10.5 Jurisdiction and data residency.** Same reasoning. Erasure semantics are already
jurisdictional in substance and not in form.

**10.6 Forensic boundary.** Crypto-shredding (ADR-0006) contradicts NIST MANAGE 2.4. Worth
noting that a forensic floor has the same monotone structure as the policy floor and could reuse
ratified machinery rather than inventing a mechanism. Belongs to ADR-0013.

**10.7 Measurement boundary.** `L` is invoked by the safety argument and never measured;
`W < L < D` has no instrumentation story. Interpretability can make `L` measurable but converts
a hard temporal property into a statistical one and couples the Observer to a model family —
which collides directly with the cross-family Observer requirement in the monoculture note.

**10.8 Invoke hermeticity.** One allowlisted tool with a shell or a socket collapses the action
alphabet to a single variant and makes the envelope vacuous. That is the vacuous-floor failure
relocated one level down. The per-tool obligation has no owner and no gate; it wants ADR-0014 or
a gate alongside floor fitness.

---

## 11. Two things to settle before anything is cited

**11.1 ADR numbering collision.** Numbers 0016 and 0017 were assigned twice on 2026.09.12 —
Persona and archetype provenance (**Accepted**, 15:22), then Build effect stream and Build action
alphabet (**Proposed**, 15:52). The no-renumbering rule protects ratified cross-references, so
the clean resolution is to renumber the Proposed pair to 0021 and 0022 and leave the Accepted
pair untouched, with a note on the face of each. Do this before either is cited anywhere.

**11.2 `Contained` may currently be empty.** Build principals are `Mediated` by the Build
alphabet record's own admission. Run principals are `Contained` only if effect exclusivity
holds, which is what §10.1 denies. As the design stands, the safety theorem inventory may be
vacuously quantified. This is not fatal — it is precisely what the sandbox layer buys back — but
it needs to be stated before a reviewer states it first.

---

## 12. Recommended sequence

1. **Persona evolution** (§8). New, unlisted, and the only uncontrolled outer cadence with no
   instant. Amendment to ADR-0016.
2. **Break-glass TTL** (§7.3). Free, reuses ratified machinery, and restores monotonicity across
   the entire authority surface. Folds into ADR-0013 rather than competing with it.
3. **Clock model** (§9.1). Cheap, and it is load-bearing under every lease and fence argument in
   the corpus.
4. **ADR renumbering** (§11.1). Trivial, and it gets more expensive with every citation.
5. **Observer quarantine gate.** Unchanged from the 09.12 next-four — still the cheapest open
   question, now blocking ordering as well as ADR-0005.
