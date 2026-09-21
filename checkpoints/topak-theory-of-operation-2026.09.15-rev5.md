# TOPAK — Theory of Operation

**2026.09.15** · revision 5 · **narrative only** · cut from Genesis Checkpoint G1 (`f46e88dafbc38f7d…`) · cleanup step 6 · findings: `NARRATIVE-LOG-2026.09.15.md` · supersedes revision 4 as narrative

---

## 0. How to read this

**This document explains how the design fits together. It is not the state of record.** Status, readiness,
digests, the ratification queue, the genesis debt ledger, and the open list are in G1. Revision 4's §0 and
§8–§11 were already superseded by G1; this revision replaces its §1–§7.

The narrative describes what the records say, whether a record is Accepted or Proposed. Status words appear only
where status changes the meaning, for example a reversal in effect.

**Findings.** Where two records disagree, or a record says less than the design needs, the text carries a marker
such as ⟨S6-2⟩. The finding and a proposed disposition are in the narrative log. A proposal described here is
marked as one; nothing in this document decides anything.

---

## 1. The pattern

TOPAK is an architecture pattern for autonomous multi-agent collaboration that is safe by design. The letters
name its five components:
- **T**, TLA+ (Temporal Logic of Actions): the formal specification and model checking;
- **O**, Open Policy Agent (OPA) and Rego: policy as code;
- **P**, Paxos: consensus over the control plane;
- **A**, agents: the principals doing the work;
- **K**, Kafka: the event transport.

**The premise.** An agent is Byzantine at every deployment position. Safety therefore cannot depend on what a
model means or intends. Models stay out of the trusted computing base (TCB), and every guarantee is stated
against an agent that may do anything its alphabet allows (ADR-0007).

**Two domains, one component.** `Build` produces artifacts; `Run` operates them. The structure is written
`Build(Contain) → Run(Contain)` (ADR-0001, ADR-0002). The arrow is authority flow. The parentheses are a
refinement boundary: specification conjunction plus existential hiding of internal variables. `Contain` is one
component instantiated twice, not a third domain. The notation does not survive being spoken, so prose has to
carry the nesting on its own.

**The inversion.** The Byzantine threat lives in Build, not Run. Build agents author the specifications, policy,
and floor that Run is later judged against. Moon & Varshney's empirical failure is a Build failure: silent
abstention, a vacuously true predicate, and green gates (§4.6 and Appendix B). Every design choice below that
looks expensive in Build is paying for that inversion.

**Principals and the gate.** *A principal is anything evictable by an authority other than itself. Whatever is
not is at the gate.* Resignation is not eviction (ADR-0002 A2). Principals are inside the proofs. Whatever is at
the gate is outside them and must be carried as an assumption or a declaration.

---

## 2. The membrane

### 2.1 What `Contain` claims

`Contain` is **boundary-enforceable containment**: two conjuncts of one statement.
1. **Proved.** A property class over the action vocabulary and its envelope, established by mechanical
   extraction.
2. **Assumed, and operationally discharged.** Effect exclusivity: the principal reaches the world only through
   the alphabet. ADR-0015 is the instrument that turns this into a mechanism claim (§4.1).

"Semantic containment" is the wrong name. It collides with ADR-0007's definition of semantic lift and asserts the
opposite of the design.

### 2.2 Syntactic lift only

A field may enter the admit path only by **syntactic lift**: mechanical, total extraction from a constrained call
interface. **Semantic lift is prohibited in the admit path** (ADR-0007). A classifier's output enters the system
only as an Observer finding, and findings may subtract authority, never add it.

Three gates keep the envelope honest: **totality**, **non-vacuity**, and **discrimination**. They run on
operational bundles and on the floor itself (ADR-0007 extension, from ADR-0010). Some desirable policies become
inexpressible at admit time and have to be restated as detections. That is the price of keeping models out of the
TCB.

### 2.3 `Contained` and `Mediated`

`Contained(p)` holds when a principal reaches the world only through its alphabet. A principal with a shell, a
package manager, network egress, or a git remote is `Mediated`: effects exist that no action names, so the
alphabet is not total. Safety theorems quantify over `Contained` principals. For `Mediated` principals the
architecture offers attribution and authorization, not containment.

**Weakest-link provenance** (candidate, unnumbered): a provenance chain that contains a `Mediated` principal
yields attribution, not a safety property.

### 2.4 Build's alphabet

Run has a typed alphabet. ADR-0022 gives Build one: **egress only**, six variants.

| Variant | Effect |
|---|---|
| `Read(ref)` | Resolve a content-addressed object inside the pinned corpus root |
| `Draft(target, content)` | Write into the round-scoped workspace |
| `Invoke(tool, inputs)` | Run a tool allowlisted by name and digest |
| `Emit(record)` | Append to the principal's round topic |
| `Submit(digest \| ⊥)` | Offer the sealed workspace for promotion, or abstain |
| `Vote(verdict, digest, evidence, rulesEpoch)` | Cast a promotion vote |

- **Every action carries epoch and lease.** Actions under a fenced epoch are rejected by the mechanism, not by
  policy.
- **Three mechanism parameters:** corpus root, tool allowlist, round bound.
- **Finite in variants, not in instances.** `Read` ranges over a large ground set, so refinement is decided over
  variants with symbolic parameters (Rego predicates checked by an SMT solver), not by enumeration.
- **`Invoke` is the whole attack surface.** One allowlisted tool with a socket collapses the envelope to vacuity.
  Each allowlist entry carries a hermeticity obligation; nobody owns it yet.
- **Seat separation.** Per artifact, the author and the voters are disjoint, and a voter in a promotion round
  cannot `Draft`, `Invoke`, or `Submit`. ⟨S6-3⟩ The alphabet states recusal as a fixed rule, while ADR-0024 reads
  it from issued rules.
- **The anchor's actions are not Build actions.** `Issue` is an environment event no Build principal can express.
  ⟨S6-9⟩

**Confinement is an obligation, not an assumption** (ADR-0022 §6): no shell, no network egress, no filesystem
outside workspace and corpus, no path to the artifactory except `Submit`. It is stated and not discharged. Until a
mechanism enforces it, **Build principals are `Mediated`**, and every Build containment theorem is conditional on
it. While this *sandbox gap* stands, `Contained` may have no members at all.

**Capability cost.** This is not how agents write code today: no shell, no package installation, no network, no
git. The article has to say so before a reader who has used a coding harness says it for us.

---

## 3. Policy

### 3.1 The verified object and the policy floor

Moon & Varshney put boundary policy inside the verified artifact. TOPAK externalizes it into signed Rego bundles
that change at runtime, and bounds them (ADR-0010).

**The verified object** is the enforcement mechanism, its version pinning, its epoch fencing, a **minimal policy
floor**, and (per ADR-0010 A1) a **minimal rules floor** (§7.3). Operational bundles are versioned parameters,
admissible only if they **refine the floor**: `bundle ⊑ floor`. They may subtract authority, never add it.

What that buys:
- **Containment is proven against the floor** and no admissible parameter can weaken it.
- **Stale bundles are monotone-safe**, bounded below by the floor at any age. Local enforcement under partition
  (EL zone 1) survives, sound by construction rather than operational care. This is the
  same shape as the lease argument.
- **Refinement is decided at promotion, in Build**, where unavailability costs a stalled pipeline rather than an
  outage.

**The floor is resident.** The default-deny bundle is pre-blessed, staged, and instantiated rather than fetched,
so fail-closed works at cold start and under partition with no network dependency (ADR-0012). It was accepted
ahead of its parent on that availability argument alone.

**The floor must stay minimal.** Its reviewability by humans at deploy cadence is the basis for trusting
promotion. A vacuous floor admits every bundle and discharges every property over nothing, invisibly: the
silent failure with the widest blast radius in the system. The gates in §2.2 run on it for that reason.

### 3.2 Changing the floor

| Change | Authority |
|---|---|
| Tighten the policy floor | An ordinary promotion |
| Relax the policy floor, or add an exception | An anchor issuance **and** a promotion |
| Any change to the rules floor | An anchor issuance **and** a promotion |

The policy floor ships inside the mechanism, and mechanism releases are promoted like any artifact (ADR-0024 §1).
Earlier text described the floor as "the one artifact verified rather than promoted." Both are true in sequence:
the floor is verified with the mechanism, and the release carrying it is promoted. The only artifact that is
never promoted is the genesis bundle (§9). ⟨S6-16⟩

### 3.3 Exceptions

Two privileged paths cannot be written as subtractions. **Erasure** (ADR-0006) destroys authority-bearing
evidence. **Break-glass** (ADR-0009) adds authority. Both are **floor exceptions**: carve-outs inside the verified
object, each with a quorum predicate proven in TLA+.

ADR-0013 writes the exception mechanism once:
- **Exceptions are declared floor entries**, each with an envelope, a roster reference, and non-composition
  obligations. Adding one is a floor relaxation.
- **The exception count is bounded** by rules-floor entry R6. The current count is two.
- **Non-composition** is stated as TLA+ invariants with mutations. **NC-1:** break-glass chained with erasure never
  yields an effect that is authorized, erased, and unattributable. **NC-2:** erasure never removes a forensic-floor
  record under any composition with break-glass.
- **Privileged grants share one authorization model:** a quorum on an anchor-issued roster, bounded by the rules
  floor. ⟨S6-13⟩ The drafted wording says *every* grant, which would include ordinary admits.

Every carve-out works against floor minimality. That tension is why the count is bounded.

### 3.4 One floor or one per class?

ADR-0010 specifies one floor shared by Build and Run. ADR-0022 shows the two domains have partially disjoint
alphabets, so a single floor is either vacuous on the variants a domain lacks, or two floors under one name. The
evidence points to **per-class floors sharing a verified core**. The same question now applies to the rules floor.
It is unresolved.

---

## 4. The record

### 4.1 Effects and authority changes are enumerated

ADR-0015 replaces an assumption with two exhaustive sets.
- **Effects:** exactly {tool invocation, principal emission}. For each, the **admit decision**, not the emission, is
  the orderable event.
- **Authority changes:** exactly {promotion, anchor issuance}. A promotion is an admit under ADR-0024. An issuance
  is an environment event validated by `Authentic` and the rules floor.

Every effect therefore has a consensus-ordered, signed, authorizing predecessor in the Paxos log. The audit chain
is

> effect → admit → `bundle ⊑ floor` → rules epoch → issuance → ADR-0025's intent axiom

and no link is assumed except the last. **Denials are not ordered:** a denied effect never crosses the boundary,
and absence of effect is not an event.

This makes **effect exclusivity a mechanism claim**, which is strictly stronger than Moon & Varshney's assumed
version and TOPAK's sharpest differentiation. It is also entirely contingent on the sandbox gap. Any sideways
effect path falsifies the enumeration rather than degrading it. ⟨S6-12⟩ Break-glass and erasure invocations still
need a place in one of the two sets.

### 4.2 What Kafka is

Kafka is **neither the ordering authority nor the system of record** (ADR-0005). It is a transport with a
durability window (`acks=all`). The causal frame comes from the Paxos log. The archive is the system of record.

ADR-0015 shrinks the remaining ordering problem to one residual: effects admitted in the same round but emitted at
different times. A per-principal sequence number may cover it. If the Observer's quarantine gate is a modeled
event, the residual closes entirely. That question gates ADR-0005.

### 4.3 Topics, payloads, erasure

**Topics.** One topic per principal per epoch or round, sealed on emit completion, with per-topic access control,
per-use-case retention, explicit replay authorization, write-time masking by wrapper Rego, and no tiered storage
(ADR-0003). The **topic is the unit of erasure**. Deleting a sealed container never edits a signature or a hash
chain, and a masking miss has a blast radius of one round. The cost is topic count, principals × rounds.

Crypto-shredding was considered and rejected: it leaves a verifying envelope over unreadable ciphertext, a hole no
auditor can tell from suppression. ⟨S6-11⟩ Three current documents still say the opposite.

**Control-plane facts and payloads.** Trace conformance needs actions, identities, and ordering, not prompt text.
Forensics needs the text. In the archive, the control-plane record keeps a hash and a pointer, and plaintext lives
in a separately governed store built for deletion (ADR-0004).

**Erasure is a modeled event** (ADR-0006): consensus-ordered, modeled in TLA+, recorded in the log it modifies. Its
authorization predicate lives in the verified object, not in a bundle. Its mechanism is deletion of sealed topics
and of plaintext-store entries. The spec obligation is a safety property that separates lawful erasure from history
rewriting.

**Replay reconstructs what crossed the membrane**, not what happened inside it (ADR-0020). The Observer and replay
read the same stream, so an investigator can never be shown something the Observer lacked at detection time. That
keeps detection latency `L` an honest number.

### 4.4 Legibility and the forensic floor

**Legibility replaces immutability.** "Immutable" lets a deployment claim conformance after erasing evidence. The
archetype property is that *every admitted boundary event remains readable by the declared audit authority for the
declared horizon.*
- HIPAA-style regimes subtract the **record** (erasure).
- SCI-style compartmentation subtracts the **reader set**, and is archetype-conformant except at spill remediation.
- The archetype log is the maximum projection each regime derives from.

**The forensic floor** (ADR-0028) makes authority facts survive erasure and break-glass. Six classes are
non-erasable for the declared horizon: **F1** admit decisions · **F2** stop attribution (e-stop, lease-expiry
eviction, `deny=all`) · **F3** promotion votes · **F4** anchor issuances, including genesis · **F5** break-glass
invocations · **F6** erasure events themselves.

- All six are control-plane facts and boundary events. **No cognitive payload is in the floor.**
- **No new primitive.** Each class is a policy-floor denial on the erasure envelope, so bundles can only narrow
  erasure further, and removing a class is a floor relaxation.
- **Compartmentation is not erasure**, provided the audit authority stays a reader.
- **Demand type 5** ("hide that a record existed") is structurally excluded at the archetype, because F6 records
  the erasure.

Two seams remain. ⟨S6-5⟩ Votes are emitted onto round topics, which are erasable as a unit, while F3 says votes are
not. ⟨S6-14⟩ The horizon is the lifetime of the rules-epoch chain, which ends at re-genesis.

**Stop attribution is non-erasable because it is a feedback path, not just evidence.** In system-theoretic terms
(STPA), the Observer is a controller, not a probe.

**At bootstrap, genesis rules issue no erasure roster.** Erasure is disabled from epoch 0 until ADR-0013 and ADR-0028
are ratified. This is fail-closed and costs nothing, since there is nothing to erase yet.

---

## 5. Detection

### 5.1 The Observer

Every semantic concern is an Observer finding, and every finding is **deny-only**: a block, a quarantine trigger,
or an eviction, never an admit precondition (ADR-0007).

**Placement** (ADR-0008). Observer replicas never share a device with the Thinker they watch, and no two replicas
share a device. A shared device means shared driver, firmware, memory error domain, thermal and power events, and
host kernel: correlated failure, and an unmodeled effect path through device memory. A Byzantine quorum of
co-resident replicas is arithmetic fiction. The Reader, which needs logits, may colocate; it was never an
independent fault domain.

**Scoping, reversed in effect.** ADR-0008 was accepted with a shared, orchestrator-level Observer group (roughly 9
model instances against 40 per-agent). ADR-0023 found that neither scoping dominates: shared Observers see
cross-principal timelines that per-principal Observers cannot. The archetype is therefore **per-principal
Observers plus a cross-principal correlator**. The strongest argument is bounded `L` and injection blast radius,
not independence of judgment. The accepted text stays in force until a superseding record exists. ⟨S6-15⟩ That
record also has to say who holds promotion veto seats.

**Monoculture.** An Observer should come from a different model family than the agents it watches. Sharing a family
is a shared blind spot.

### 5.2 Build has an Observer

A hostile domain with enforcement and no detection was the sharpest contradiction on the board. ADR-0021 closes it
by reusing Run's round-topic scheme:
- **A Build round is one pipeline invocation.** Each principal seat holds its own topic.
- **Sealing moves to submission.** The principal's topic set is sealed when the artifact is submitted.
- **Retention diverges by parameter.** Build topics live as long as any artifact promoted from them. The mechanism
  is the same.
- **Build's Observer follows ADR-0008 placement**, cross-family, deny-only.

**Timing runs the right way.** Run's `W < L < D` chain is hard: the propagation window is about a second and no
human fits inside it, so Run is human-on-the-loop (HOTL). Build favors consistency over latency and its promotion
gate blocks, so Build detection only has to finish before the gate clears. Detection is cheaper in Build, which
makes its absence harder to defend. ⟨S6-8⟩ ADR-0021 still describes a single human approver.

### 5.3 What logprobs can and cannot do

Interpretability can make `L` measurable, but only statistically, which turns a hard bound into a confidence
bound. White-box Observers also raise model-family coupling, against the monoculture rule. ADR-0019's narrow form
(§6) guards against drifting there by accident.

---

## 6. The model is pinned

Before the Persona series, everything in the system was pinned except the model. ADR-0016 to ADR-0020 close that
asymmetry.

- **The Persona** (0016) binds a model to its complete runtime configuration: provenance and cryptographic
  identity, system prompt, decoding parameters, decoder identity and hash, decode-observability class, and seat
  binding. It is a verified artifact.
- **The archetype admits only in-house pre-trained Personas** from two independent lineages (0017). Overlapping
  public corpora do not count as independent. The admission clause stands; its ordering-primacy clause is reversed
  in effect by ADR-0023 (§8.3).
- **The typed lift splits** (0018). The model-specific decoder ships in the Persona; the model-agnostic validator
  lives in the mechanism. This is the ADR-0010 move (verified core, parameterized edge) applied to syntax.
- **Decode observability is narrow** (0019). `none` is the only unconditional value. `topk_logprobs` is admissible
  for decoding conformance and substitution detection only, never for claims about `L`.
- **Replay scope is boundary events only** (0020), with explicit revisit triggers.

Havoc semantics still make a *worse* model harmless for containment. What changes is that silent substitution
becomes a detectable identity mismatch instead of an unmodeled event. None of these records adds a floor
exception: revocation, decoder failure, and subtraction are all denies.

---

## 7. Authority

### 7.1 Promotion is a quorum grant

The single promotion signing key was the last privileged human grant. ADR-0024 replaces it.

- **Promotion is a grant.** Everything crossing from Build to Run is promoted: bundles, mechanism releases
  (including floor changes), and Personas.
- **The quorum rule is read from issued rules.** At the archetype, every counted grant seat must grant. A grant-seat
  deny or abstention denies. **A timeout is never a grant**, as a mechanism constant.
- **Seat classes.** *Grant seats* are human `Mediated` principals with named organizational roles. *Veto seats* are
  held by the independent Observer and can only deny. Under unanimity every seat is a veto; a veto seat is one whose
  alphabet lacks `grant`.
- **Veto-seat silence is not a veto.** Requiring an Observer "no finding" attestation would make semantic judgment an
  enabling condition, which ADR-0007 forbids.
- **Votes bind to (artifact digest, gate-evidence digest, rules epoch).** Any rules-epoch change voids in-flight
  votes: fencing, the same shape as leases.
- **Gates enable voting; they do not vote.** `Vote` is enabled only after the ADR-0007 gates and `bundle ⊑ floor` pass.
- **The author is recused.** If recusal leaves fewer seats than the floor minimum, promotion is denied.
- **Runtime subtraction is not promotion.** E-stop, lease expiry, and `deny=all` stay local and attributed.

Promotion now obeys consensus-for-grants like every other grant, and no strict subset of grant seats can promote.
Two costs are stated in the record. **Liveness equals the availability of every grant seat.** **Correlated review
failure is untouched:** unanimous humans reading the same vacuous gate output fail together (Moon & Varshney §4.6;
Knight & Leveson). Floor fitness, a fourth gate (NIST MEASURE 2.13), is still unowned.

⟨S6-5⟩ Where the authoritative vote record lives is unsettled. ⟨S6-8⟩ Promotion is defined as a round under
ADR-0021, which is queued separately.

### 7.2 The trust anchor is a havoc issuer

Promotion moves the gate up one level: the authority defining who votes cannot itself be voted in without regress.
ADR-0025 weighed three treatments of that authority, the **trust anchor**: infallible (an oracle), havoc (any
authentic issuance, bounded by a verified floor), or characterized (havoc plus a model of how members decide).

Under havoc, safety is proven for every issuance the anchor could make, so the anchor's composition never enters
the proof. The decision is **havoc, with "infallible" split three ways**:

| Property | Treatment |
|---|---|
| **Intent** | **Assumed**, the sole axiom: *an authentic issuance at the current anchor epoch is what the anchor intended.* |
| **Integrity** | **Modeled**: `Issue` is an environment action bounded by an opaque `Authentic`, epoch increment, and the rules floor |
| **Custody** | **Declared** per deployment position: the pair (capture threshold, loss tolerance) |

**Rules** are the authority-defining set: the promotion roster and its parameters, the break-glass and erasure
rosters, the anchor's own key set, and any relaxation of the policy floor or new exception. ⟨S6-6⟩ The record's
wording leaves rules-floor changes out of this list and says "the floor" where it means the policy floor.

**Custody is a declaration axis** (anchor recoverability):

| Record | Custody model | (capture, loss) |
|---|---|---|
| A-0025 (archetype) | Strict unanimity, n ≥ 3 | (n, 0) |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) |
| D-0025-1 | Threshold with recovery, in the shape of The Update Framework (TUF) root role | (k, n−k) |
| — | Single custodian | (1, 0) |

At the archetype, **loss freezes the rules**: the system runs and subtracts but cannot change, and the only exit is
**re-genesis**, which creates a successor system. That fragility pushes operators toward degenerate custody, which is
correct as long as it is declared. **The headline residual:** a coalition at the capture threshold can issue any
rules-floor-conformant roster. No safety theorem covers anchor intent.

### 7.3 The rules floor bounds the anchor

Havoc over rules without a bound is havoc over authority: an issuance could set a roster of one. ADR-0026 applies
ADR-0010's move one layer up. The rules floor joins the verified object, and the mechanism rejects any issuance
that violates it.

| Entry | Bound |
|---|---|
| R1 | `quorum = "all"` over counted grant seats |
| R2 | `minGrant ≥ 2` |
| R3 | `recuse = TRUE` |
| R4 | *Withdrawn*: a timeout never grants, now a mechanism constant |
| R5 | No key both in the anchor key set and on the promotion roster |
| R6 | Exception-count bound (arrives with ADR-0013) |
| R7 | No break-glass grant may authorize `Issue`, `Vote`, or promotion |

**Parametricity is load-bearing.** A floor entry bounds something only if the mechanism reads that value from
issued rules. The 2026.09.15 non-vacuity run (`RulesFloorNV`, TLC) showed it:
- Against ADR-0024 revision 3, which hard-coded the values, R1–R3 constrained nothing.
- Against revision 4, every entry has a mutation that fails, promotion is reachable, and all properties hold.
- **Dropping R2 promotes with zero votes.** A havoc issuance sets an empty roster, and unanimity over the empty set is
  vacuously true. R1 alone does not protect against an empty roster.

⟨S6-2⟩ The parameters cannot express a k-of-n threshold, so one declared degeneracy is unreachable. ⟨S6-3⟩ The Build
alphabet still hard-codes recusal, which is the vacuity pattern the run was designed to catch. Both change mechanism
text, and the run has to be repeated after they are settled.

**Two keys, both directions.** A rules-floor change needs an anchor issuance and a promotion under the rules being
replaced. Tightening needs both too, because a tightened rules floor constrains the anchor, which must consent. That
is where the rules floor differs from the policy floor.

### 7.4 Genesis rules are resident

At cold start or under partition the anchor may be unreachable. If genesis rules were fetched, every grant path
would block. ADR-0027 applies ADR-0012's argument to rules: **genesis rules ship with the mechanism release and are
fetched from nowhere.** Anchor unavailability blocks change, never operation. Epoch 0 is the root of the rules-epoch
chain.

The cost is stated: a compromised genesis is a compromised system, covered only by the intent axiom. ⟨S6-4⟩ The
record says genesis rules are checked at promotion, but genesis is never promoted. ⟨S6-17⟩ It also assumes, without
saying, that later issued rules are resident too.

### 7.5 Who is at the gate

- **At archetype custody,** anchor key-holders are removable only with their own consent, so they sit at the gate.
  They are attributable non-principals; `Mediated` applies to them as attribution only.
- **At degenerate custody,** the genesis threshold or eviction rule can remove a key-holder, so key-holders become
  principals and the gate moves to that rule. That is a type change, and it moves the TCB (§8.2).
- **Promotion voters are principals on every rung**, because the anchor can evict them. Promotion therefore enters
  `Build(Contain)` enforcement coverage.

⟨S6-7⟩ ADR-0002's drafted amendment says "the anchor is at the gate" without the custody qualifier.

The system-under-test versus system-testing cut runs *inside* each domain, and the evictability test is its carrier
at boundary B14. Casting Build as the test apparatus would invert the trust relation ADR-0010 refused.

### 7.6 How the regress ends

The corpus has described the end of Build's trust regress three ways, and they are stages of one argument.

| Record | Terminus |
|---|---|
| ADR-0002 (09.12) | A declared axiom set |
| ADR-0010 (09.12) | A verified artifact, the policy floor, rather than an axiom set |
| ADR-0025 with ADR-0026 | **One axiom (anchor intent), bounded by two verified floors** |

The authority regress now ends the way the policy regress does: a verified floor, with a single sentence assumed
above it.

### 7.7 Modeled versus declared

**A promotion degeneracy is a mechanism release; a custody degeneracy is a declaration.** The quorum's archetype
values live inside the rules floor, inside the verified object, so degrading them changes what the mechanism admits
and reopens the promotion theorem. Custody instantiates the opaque `Authentic` outside the model, so degrading it
reopens nothing. The two axes, approver fault tolerance and anchor recoverability, are declared independently.

### 7.8 Monotonicity at five layers

| Layer | Statement | Source |
|---|---|---|
| Decision | Consensus for grants, local for denials | Established |
| Policy | Bundles only subtract from the floor | ADR-0010 |
| Change | Authority-increasing changes need consensus; decreasing ones are local and attributed | Floor-rollout session |
| Deployment | Degenerate forms lose theorems, never gain capability | ADR-0023 |
| Authority | Relaxing rules needs the anchor; operating within them does not | ADR-0025, ADR-0026 |

**At the pattern level it inverts.** Tightening the archetype puts every conformant deployment into declaration
debt. Relaxing it voids published theorems. Both directions cost something.

---

## 8. Deployment variation

### 8.1 Degeneracy, not a ladder

Three demotion proposals arrived within 48 hours on three parameters: Persona provenance, event-log legibility, and
Observer scoping. They were not comparable, and two reversed accepted records. The ladder was only ever true on one
axis. ADR-0023 replaces it:

- **Degeneracy.** D is a degenerate form of archetype A if D is obtained by driving named parameters to limiting
  values. *Degenerate* is the formal register; *reduced* is the operational one.
- **Effect is premise loss, not weakening.** Theorems are present or absent.
- **The archetype is the unique maximum** of the parameter lattice: a reference point, not a shippable
  configuration.
- **Admission test.** A variation is a rung only if it is reachable from A by parameter limit. If it has a capability
  A lacks, **A is incomplete**, and the rejection is a finding about the archetype.
- **Rungs are per-axis.** A deployment is a tuple; unqualified "rung demotion" is barred.
- **Every degeneracy carries a declaration record** with a fixed schema: parameter, archetype value, deployed value,
  premises falsified, theorems voided, optional mitigation, and a composition note above one parameter.

**Nobody ships the archetype.** The TLA+ theorems are proved about an unshipped configuration. The article must say
so, with ISO 26262's safety element out of context (SEooC) as the precedent.

### 8.2 What the lattice has learned since

- **Axes named so far:** Persona provenance, event-log legibility, Observer scoping, effect-stream role, arguably
  HITL/HOTL/HOOTL posture, approver fault tolerance, and anchor recoverability. The set is not enumerated, and
  finiteness of each chain is unproven.
- **Two kinds of degeneracy** (§7.7). The declaration schema should record which kind.
- **Admission must check type changes, not only voided theorems.** A degeneracy can move a participant from the gate
  to principal.
- **Archetype versioning.** The archetype grows on failed admission, so conformance binds to (archetype version, rung
  tuple), and published versions freeze.
- **Dominance rule.** The archetype moves on a paired axis only to Pareto-dominating values.
- **Non-increasing TCB** across archetype versions. Moving a property into *assumed* needs its own record.
- **Composition** is not assumed monotone: two degeneracies may void more than the union of their theorem sets.
  Composition over the lattice belongs to ADR-0023.

Declared records so far: **D-0024-1** (k-of-n grant seats) and **D-0024-2** (single signer) on approver fault
tolerance; **A-0025**, **D-0025-1**, and **D-0025-2** on anchor recoverability. ⟨S6-2⟩ D-0024-1 fails the admission
test against the current mechanism, which by the test's own rule is a finding about the archetype.

### 8.3 Reversals in effect

- **ADR-0008's shared Observer scoping** (§5.1). A superseding record is required.
- **ADR-0017's ordering-primacy clause.** Provenance as *the* deployment axis cannot survive per-axis rungs. The
  admission clause stands.

Both reversals happened during genesis, within 48 hours, by the author alone. That is part of why their superseding
records will need independent confirmation (§9).

---

## 9. Genesis: the corpus governs itself

TOPAK claims its governance is recursive: Build is a system with its own TOPAK. ADR-0029 applies that claim to the
design process.

**The current process is genesis, not a degeneracy.** Before the anchor exists there is no archetype custody to
degenerate from. Genesis custody is declared: Scott, sole custodian, (1, 0). Everything ratified in genesis is
trusted by declaration and becomes part of the genesis TCB.

**Ratification is unilateral, and the risky part is tracked as debt.**
- The custodian may ratify any record with decision text. A record without decision text cannot be ratified.
- A ratified record is marked **confirmation-required** if it carries a proof obligation over privileged paths (C1),
  an exhaustiveness or confinement claim (C2), a reversal in effect of an accepted record (C3), or resolves a debt
  owed by one (C4).
- **The bootstrap set (ADR-0024 to 0027) cannot be confirmation-required.** Confirmation runs under those rules, and
  confirming them under themselves would be circular.
- Until confirmed, a publication citing a confirmation-required guarantee says "author-ratified."

**Bootstrap trigger.** The anchor may bootstrap once a drafted TLA+ bootstrap specification exists: five modules
(`Genesis`, `Anchor`, `RulesFloor`, `Promotion`, `BreakGlass`), five invariants, and a mutation for each that must
fail. `RulesFloorNV` is a precursor, not a substitute.

**Ceremony.** Seat key-holders under a declared custody record. Assemble the **genesis bundle**: the corpus manifest,
including the confirmation-required set; the specification digest, marked checked or drafted-only; and the genesis
rules. Every key-holder signs its digest. That is issuance epoch 0. **The genesis bundle is the only artifact never
promoted.**

**After bootstrap,** each confirmation-required record goes through a confirmation promotion under ADR-0024 with author
recusal. Confirmed records lose the marker; rejected ones need a superseding record. Genesis records without the
marker are not re-reviewed.

**No forcing function.** Genesis may last indefinitely. In its place, every checkpoint carries a debt ledger (G1 §8).
The debt is visible, not bounded.

**Headcount.** ADR-0029 puts an archetype bootstrap at no fewer than five humans. The corpus supports that figure
without stating the derivation: three anchor key-holders (A-0025), two counted grant seats (R2), and disjointness
between them (R5). A solo bootstrap is not a bootstrap. ⟨S6-10⟩ The non-vacuity run's
smallest model has four humans and is labeled as the genesis headcount; its one anchor key-holder is custody (1, 0).

**What the cleanup taught.** The freeze, recovery, fold, normalization, and G1 treated the corpus the way the pattern
treats artifacts: records identified by digest, changes recorded as typed history, and nothing applied that was not
ratified. Every pass found something the previous pass had missed, including this one. That is the practical form of
ADR-0029's weakest point: **the bootstrap set gets no independent review, ever**, so the only reviews it receives
are the author's passes before ratification.

---

## 10. Boundaries and assumptions

The **boundary register** lists fourteen boundaries, each with its cadence, its instant, its interval of untruth, and
its behavior when unavailable.

- **B8, Persona evolution, is the most critical:** an uncontrolled outer cadence with no instant. Apple Private Cloud
  Compute is a shipped counterexample showing it can be controlled.
- **Break-glass grants have no TTL expiry**, which breaks the monotonicity claim. A TTL is a candidate rules-floor
  entry (R8).
- **The clock model is unstated.** Leases, fencing, and vote timeouts all rest on it. Gray and Cheriton leases and
  RFC 9334 give a standard answer, so this is open with a known answer.
- **`Contained` may have no members** while the sandbox gap stands.

**The register's assessment,** in brief. Strong: the unavailability column, cadence as a first-class axis, the CALM
result, and reading the register by its holes. Weak: no per-boundary adversary, no owner column, fail-closed
uniformity presented as costless, SLSA re-derived without citation. Uncomfortable: Knight and Leveson's evidence that
independence is empirically weak, and no timing budget for what is effectively a real-time safety architecture.

**Highest-leverage fix:** put **assumptions of use at the front**, framed as a safety element out of context. That
converts the largest weaknesses from omissions into declared conformance.

---

## 11. External alignment

### 11.1 Moon & Varshney (arXiv:2605.09045v2)

**Concordant:** havoc semantics; the containment and oracle split; ADR-0007 matching their boundary-enforceable
property class.

**Extended:** ADR-0010's floor plus refinement, since the paper never addresses policy change cadence; ADR-0015's
mechanism claim for effect exclusivity; the rules floor, which carries the same move to authority.

**Exposed:**
1. Their failure result is in §4.6 and Appendix B, not §4.2. Citations are corrected or queued for correction.
2. **Three gates are insufficient by their own published result.** A fourth, floor fitness, is required and unowned.
3. The sandbox gap, which can be restated in the paper's deployment-stack vocabulary.
4. Theorem versus corollary alignment in the `Contained`/`Mediated` split.
5. Their Figure 1 covers Run only. Build's substrate rests on trusting-trust and supply-chain (SLSA) concerns, so
   either a second diagram or an explicit acknowledgment is needed.

The co-author's name is spelled **Varshney**. Check any draft outside the Project before publishing.

### 11.2 NIST AI Risk Management Framework (AI RMF) Playbook

Two artifacts map TOPAK to the Playbook: the 09.12 delta inventory (historical; its tally was wrong) and the 09.15
feature list, with 48 features under eight principles and the corrected tally. Both are regenerated in step 7.

The narrative expectation for that pass:
- **MANAGE 3.2** should move from gap toward met, on the Persona series.
- **GOVERN 3.2** strengthens on ADR-0024 and the evictability test.
- **GOVERN 1.3 and MAP 1.5** convert, since ADR-0023 resolves the axis question.
- **MANAGE 2.4** is resolved by mechanism: legibility, non-erasable stop attribution, and the forensic floor.
- **Still gaps:** MAP 2.3 (TLC versus TLAPS undeclared), MAP 3.4 (operator proficiency), MEASURE 2.13 (floor
  fitness), MEASURE 3.2 (`L`), MANAGE 1.4 (residual-risk statement, headed by anchor capture), MANAGE 3.1
  (monoculture).

### 11.3 TLA+ practice

- **`Voting` is a mandatory abstraction layer** between `Consensus` and `Paxos`.
- **`ENABLED Deny(a)` is a checkable invariant** for consensus-for-grants and local-for-denials.
- **HITL, HOTL, and HOOTL are `ENABLED` predicates.**
- **`W < L < D` is only partly expressible** in standard TLA+.
- **No non-vacuity gate exists for TLA+ invariants**, mirroring the Rego vacuity problem one layer down. The
  `RulesFloorNV` reachability witness is the shape such a gate would take.

---

## 12. Where the argument is thin

The open list is G1 §9. In narrative terms, the argument is weakest in six places.

1. **The sandbox gap.** Effect exclusivity, 0015's exhaustiveness, and 0022's confinement all rest on a mechanism
   nobody has specified. Until it exists, the strongest claim TOPAK makes is an assertion.
2. **Correlated review failure.** Unanimity multiplies reviewers without making them independent. Floor fitness is
   the missing gate.
3. **ADR-0013.** Two ratified records owe it their privileged-path proofs, and it has no decision text.
4. **Anchor capture.** The residual is real, numeric, and the first line of any residual-risk statement.
5. **The archetype is unshipped.** Every theorem is about a configuration no one deploys, which is honest only if
   the declaration records are actually written.
6. **The bootstrap set as drafted.** This pass found nine issues in records queued for ratification without
   independent review (narrative log §2). All are in-place revisions, and two require repeating the non-vacuity run.

---

## Appendix A. Changes from revision 4

- **State of record removed.** Ledger, ADR log, open list, genesis plan, and next steps are in G1.
- **Revision 4 §1 (numbering) removed.** It is history, and G1 carries the resulting records.
- **Revision 4 §5.6 and §5.7** (drafted changes; ADR-0025 decomposition) folded into §7 and §8 as design, with the
  queue in G1 §7.
- **New narrative:** §2.3 `Contained`/`Mediated`, §3.2 floor-change table, §3.3 exceptions, §4 the record end to end,
  §7.6 how the regress ends, §9 genesis.
- **Findings markers** ⟨S6-2⟩ to ⟨S6-17⟩ added where records disagree.
- **Recount table and movement table** from revision 4 §7.2 dropped; they are regenerated in step 7.
