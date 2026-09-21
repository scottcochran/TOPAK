# TOPAK — Glossary

**2026.09.17** · derived · regenerated from scratch · *The Gripping Hand*

**Basis.** Theory of Operation revision 5 (2026.09.15), Genesis Checkpoint G1 (2026.09.15), the
boundary register (2026.09.13), the critical review (2026.09.16), and the narrative log
(2026.09.17). Session material from 09.16–09.17 that has not reached a record is included and
marked, because the vocabulary is already in use in conversation.

**What this supersedes.** The 2026.09.11 glossary, which G1 §4 placed outside the corpus as stale.
Nothing from it is folded in; every entry below is re-derived. This is cleanup **step 7**, the
glossary half.

**This document decides nothing.** It reports what terms mean in the corpus as it stands, including
where two records disagree.

---

## 0. How to read

Each entry carries a bracket that says what kind of thing it is. The bracket is about the *term*,
not about whether the design is good.

| Tag | Meaning |
|---|---|
| **[A]** | Defined by an Accepted (genesis) record |
| **[P]** | Defined by a Proposed or Draft record; the wording can still move |
| **[D]** | Derived — used throughout the narrative, no record of its own |
| **[O]** | Outstanding — the term currently names a hole rather than a mechanism |
| **[C]** | Checkpoint convention — fixed by G1, which "ratifies nothing and adds no decision text" |
| **[S]** | Session vocabulary — coined 09.16–09.17, in no record and in no checkpoint |
| **[X]** | Dangling — in use, with no source that defines it |

Status of the underlying record is G1 §2 and is not restated here except where status changes the
meaning. **Confirmation-required** and readiness keys are §10.

Three companion sections close the document: **§11 Outstanding**, the terms that are holes;
**§12 Adjacent**, the vocabulary readers arrive with; **§13 Hazards**, the collisions to settle
before publication. **§14** lists retired wording — the reason the last glossary went stale.

---

## 1. The pattern and its letters

**TOPAK** [A/D] — an architecture pattern for autonomous multi-agent collaboration that is safe by
design. The letters name five components, not five domains:

| Letter | Component | Role in the pattern |
|---|---|---|
| **T** | TLA+ (Temporal Logic of Actions) | Formal specification and model checking |
| **O** | Open Policy Agent (OPA) and Rego | Policy as code |
| **P** | Paxos | Consensus over the control plane |
| **A** | Agents | The principals doing the work |
| **K** | Kafka | Event transport |

Components are one instantiation, not the pattern. A component is substitutable by **role
obligation**, not by feature parity: anything that discharges the role's obligations may stand in
its place. The critical review (§2.7) recommends naming the *requirement* — for O, a policy
language with a verified evaluator and decidable refinement — and naming Cedar as the reference
instantiation, keeping OPA where a deployment already has it.

**The premise** [A] — *an agent is Byzantine at every deployment position.* Safety never depends on
what a model means or intends. This is the single premise the whole derivation runs on (ADR-0007).

**The inversion** [D] — the Byzantine threat lives in **Build**, not Run. Build principals author
the specifications, policy, and floors that Run is later judged against. Every Build cost in the
design is paying for this. The field's counterpart systems all assume the policy author is trusted;
this is TOPAK's unoccupied ground.

**Safe by design** [D] — the project's own descriptor. Means *containment proven about the
mechanism*, never *safe outputs*. Without that scope line the phrase claims output safety and is
indefensible.

**Verify the cage, not the occupant** [D] — principle P1, the pattern's slogan form.

---

## 2. Domains, membrane, principals

**`Build`** [A] — the domain that produces artifacts. Renamed from CI by ADR-0001, which retired the
continuous-integration / critical-infrastructure ambiguity. Consistency posture PC/EC: unavailability
costs a stalled pipeline.

**`Run`** [A] — the domain that operates artifacts. Formerly Orch.

**`Contain`** [A] — the containment component. One component instantiated twice, **not** a third
domain.

**`Build(Contain) → Run(Contain)`** [A] — the structural expression of the above (ADR-0001,
ADR-0002). The arrow is authority flow. The parentheses are a refinement boundary: specification
conjunction plus existential hiding of `Contain`'s internal variables. **The notation does not
survive being spoken**, so prose must carry the nesting on its own.

**Boundary-enforceable containment** [A] — what `Contain` claims, as two conjuncts of one statement:
a **proved** property class over the action vocabulary and its envelope, established by mechanical
extraction; and an **assumed, operationally discharged** effect exclusivity. The correct name for
the claim. "Semantic containment" is wrong and is retired (§14).

**Membrane** [D] — the informal name for `Contain` as it appears inside `Run`. "Contained spatially,
excluded epistemically."

**Principal** [A] — *anything evictable by an authority other than itself.* One type for agents and
humans. Principals are inside the proofs.

**At the gate** [A] — whatever is not evictable. Outside the proofs, carried as an assumption or a
declaration. **Resignation is not eviction** (ADR-0002 A2), which is why anchor key-holders sit at
the gate at archetype custody.

**Evictability test** [A] — the criterion above, applied. The sharpest definition in the design, and
the reason boundary B14 exists.

**`Contained(p)`** [D/P] — holds when a principal reaches the world only through its alphabet.
Safety theorems quantify over `Contained` principals only.

**`Mediated(p)`** [D/P] — a principal with a shell, a package manager, network egress, or a git
remote: effects exist that no action names, so the alphabet is not total. For these the architecture
offers **attribution and authorization, not containment**. Humans are never `Contained`.

**Weakest-link provenance** [O] — candidate, unnumbered, carried in ToO rev 5 §2.3 and G1 §2: a provenance chain containing a `Mediated`
principal yields attribution, not a safety property. One sentence; the critical review recommends it
become a clause of the ADR-0008 or ADR-0023 supersession rather than a record.

**Action alphabet** [A/P] — the finite, typed vocabulary of a principal's effects. Run has one;
ADR-0022 gives Build one.

**The Build alphabet** [P] — **egress only**, six variants: `Read(ref)` · `Draft(target, content)` ·
`Invoke(tool, inputs)` · `Emit(record)` · `Submit(digest | ⊥)` · `Vote(verdict, digest, evidence,
rulesEpoch)`. Every action carries epoch and lease. Three mechanism parameters: corpus root, tool
allowlist, round bound.

**Finite in variants, not in instances** [P] — `Read` ranges over a large ground set, so refinement
is decided over variants with symbolic parameters (Rego predicates checked by a satisfiability
modulo theories, or SMT, solver), never by enumeration.

**`Invoke` hermeticity** [O] — the per-allowlist-entry obligation that a tool opens no effect path
the alphabet does not name. **One allowlisted tool with a socket collapses the envelope to vacuity.**
No owner, no gate. One of the two unowned gates that decide whether the whole envelope means
anything (the other is floor fitness, §3).

**Seat separation** [P] — per artifact, author and voters are disjoint; a voter in a promotion round
cannot `Draft`, `Invoke`, or `Submit`. ⟨S6-3⟩ the alphabet states recusal as a fixed rule while
ADR-0024 reads it from issued rules.

**Confinement obligation** [P] — ADR-0022 §6: no shell, no network egress, no filesystem outside
workspace and corpus, no path to the artifactory except `Submit`. **Stated and not discharged.**
Until a mechanism enforces it, Build principals are `Mediated`.

**Capability cost** [D] — the admission that this is not how agents write code today: no shell, no
package installation, no network, no git. The critical review argues the cost may be smaller than
stated if the sandbox boundary is modeled as `Invoke`'s hermeticity envelope, since a shell whose
only reachable effects are workspace writes is observationally `Draft`.

---

## 3. Policy and the floors

**Syntactic lift** [A] — mechanical, total extraction of a field from a constrained call interface.
The only way a field may enter the admit path, and **permitted in any zone**.

**Semantic lift** [A] — a model's judgment entering the admit path. **Prohibited** (ADR-0007). A
classifier's output enters only as an Observer finding, and findings may **subtract authority, never
add it**.

**The three gates** [A] — run on operational bundles *and* on the floor itself: **totality** (the
alphabet covers every reachable call), **non-vacuity** (the envelope constrains something reachable),
**discrimination** (it separates cases that must be separated). Referred to as G1–G3 in review
material, which collides with the genesis checkpoints — see §13.

**Floor fitness** [O] — the missing fourth gate (NIST MEASURE 2.13). Three gates are insufficient by
Moon & Varshney's own published result: a vacuous specification passes all three. **Unowned.**

**Verified object** [A, with an unratified amendment] — the enforcement mechanism, its version
pinning, its epoch fencing, and the minimal **policy floor**. ADR-0010 **A1 would add the minimal
rules floor; it is Pending, triggered by ADR-0026, and queued in batch B.** Everything else is a
versioned parameter. Each addition is a reviewability cost under ADR-0010's own minimality argument.

**Policy floor** [A] — the minimal, default-deny, human-reviewable bundle inside the verified
object. Containment is proven against it.

**`bundle ⊑ floor`** [A] — refinement. An operational bundle is admissible only if it refines the
floor; it may subtract authority, never add it. Decided **at promotion, in Build**, where
unavailability costs a stalled pipeline rather than an outage.

**Monotone-safe staleness** [D] — the consequence: a stale bundle is bounded below by the floor at
any age, so local enforcement under partition is sound by construction rather than by operational
care. The model case in the boundary register's interval table, and the shape the lease argument now
copies.

**Resident floor** [A] — the default-deny bundle is pre-blessed, staged, and **instantiated rather
than fetched**, so fail-closed works at cold start and under partition with no network dependency
(ADR-0012).

**Vacuous floor** [D] — a floor that admits every bundle and discharges every property over nothing,
invisibly. The silent failure with the widest blast radius in the system, and the reason the gates
run on the floor.

**Rules floor** [P] — the bound on the trust anchor (ADR-0026). Joins the verified object; the
mechanism rejects any issuance that violates it.

| Entry | Bound |
|---|---|
| R1 | `quorum = "all"` over counted grant seats |
| R2 | `minGrant ≥ 2` |
| R3 | `recuse = TRUE` |
| R4 | **Withdrawn** — a timeout never grants; now a mechanism constant |
| R5 | No key both in the anchor key set and on the promotion roster **for the same artifact** (the qualifier is in ADR-0026 and dropped by ToO rev 5 §7.3) |
| R6 | Exception-count bound (arrives with ADR-0013) |
| R7 | No break-glass grant may authorize `Issue`, `Vote`, or promotion |
| R8 | **Candidate** — break-glass time-to-live; asked for since 09.13 |

**Parametricity** [P] — a floor entry bounds something only if the mechanism **reads that value from
issued rules**. Hard-coded values make the entry vacuous. Established mechanically by the
`RulesFloorNV` run.

**Empty-roster promotion** [P] — the corpus's sharpest checked result: drop R2 and a havoc issuance
sets an empty roster, unanimity over the empty set is vacuously true, and an artifact promotes with
**zero votes**. R1 alone does not protect against it.

**Floor exception** [P] — a carve-out inside the verified object for a path that cannot be written as
a subtraction. Two exist: **erasure** (destroys authority-bearing evidence) and **break-glass** (adds
authority). Each is a declared floor entry with an envelope, a roster reference, and non-composition
obligations. Adding one is a floor relaxation. Count bounded by R6.

**Non-composition** [P] — the obligations stated as TLA+ invariants with mutations. **NC-1:**
break-glass chained with erasure never yields an effect that is authorized, erased, and
unattributable. **NC-2:** erasure never removes a forensic-floor record under any composition with
break-glass. Both are currently **untimed**, and the register argues the interval between the two
orderings is part of the property.

**Per-class floors** [O] — the unresolved question of whether Build and Run share one floor or have
one each over a shared verified core. ADR-0022's partially disjoint alphabets are the evidence; the
same question now applies to the rules floor.

---

## 4. Authority

**Promotion** [P] — the crossing from Build to Run, for everything: bundles, mechanism releases
(including floor changes), and Personas. **Promotion is a grant**, and under ADR-0024 it is a quorum
grant read from issued rules, not a signing key.

**Grant seat** [P] — a human `Mediated` principal with a named organizational role, whose vote is
counted. At the archetype every counted grant seat must grant; a deny or an abstention denies.

**Veto seat** [P] — held by the independent Observer; can only deny. A veto seat is one whose
alphabet lacks `grant`. **Veto-seat silence is not a veto** — requiring a "no finding" attestation
would make semantic judgment an enabling condition, which ADR-0007 forbids.

**A timeout is never a grant** [P] — a mechanism constant, not a policy.

**Vote binding** [P] — votes bind to (artifact digest, gate-evidence digest, rules epoch). Any
rules-epoch change voids in-flight votes: fencing, the same shape as leases.

**Gates enable voting; they do not vote** [P] — `Vote` is enabled only after the three gates and
`bundle ⊑ floor` pass.

**Recusal** [P] — the author of an artifact is recused from voting on it. If recusal leaves fewer
seats than the floor minimum, promotion is denied.

**Runtime subtraction is not promotion** [P] — e-stop, lease expiry, and `deny=all` stay local and
attributed.

**Trust anchor** [P] — the authority that defines who votes. Treated as a **havoc issuer**: safety is
proven for every issuance it could make, so its composition never enters the proof (ADR-0025).

**Issuance** [P] — an anchor action. An environment event validated by an opaque `Authentic`
predicate, an epoch increment, and the rules floor. `Issue` is not a Build action and no Build
principal can express it. ADR-0022 §8 gives the anchor's alphabet as **`Issue` and `Resign`** —
⟨S6-9⟩ `Resign` is cited there and **defined nowhere**, which matters most at archetype custody,
where a resignation is a permanent loss and therefore a freeze.

**Rules** [P] — the authority-defining set: the promotion roster and its parameters, the break-glass
and erasure rosters, the anchor's own key set, and any relaxation of the policy floor or new
exception. ⟨S6-6⟩ the record's wording omits rules-floor changes from this list.

**The intent axiom** [P] — the sole axiom: *an authentic issuance at the current anchor epoch is
what the anchor intended.* The end of the authority regress.

**Infallible, split three ways** [P] — **intent** assumed, **integrity** modeled, **custody**
declared. The recurring decomposition shape (see §5 and §7).

**Custody** [P] — the declared pair (capture threshold, loss tolerance), an axis of anchor
recoverability:

| Record | Model | (capture, loss) |
|---|---|---|
| A-0025 | Strict unanimity, n ≥ 3 — the archetype | (n, 0) |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) |
| D-0025-1 | Threshold with recovery, in the shape of The Update Framework (TUF) root role | (k, n−k) |
| — | Single custodian | (1, 0) — the row the corpus itself occupies, with no deployment declaration record |

**Loss freezes the rules** [P] — at archetype custody, the system runs and subtracts but cannot
change. The only exit is re-genesis.

**Anchor capture** [P] — the headline residual: a coalition at the capture threshold can issue any
rules-floor-conformant roster. **No safety theorem covers anchor intent.** First line of any
residual-risk statement.

**Two keys, both directions** [P] — a rules-floor change needs an anchor issuance *and* a promotion
under the rules being replaced. **Tightening needs both too**, because a tightened rules floor
constrains the anchor, which must consent. This is where the rules floor differs from the policy
floor.

**Genesis rules** [P] — ship with the mechanism release and are **fetched from nowhere** (ADR-0027).
Anchor unavailability blocks change, never operation. Epoch 0 is the root of the rules-epoch chain.

**Monotonicity, at five layers** [D] — decision (consensus for grants, local for denials) · policy
(bundles only subtract) · change (authority-increasing needs consensus; decreasing is local and
attributed) · deployment (degenerate forms lose theorems, never gain capability) · authority
(relaxing rules needs the anchor). **⟨LP-9⟩ proposes a sixth:** an attenuation rule for derived
principals. **At the pattern level it inverts** — tightening the archetype puts every conformant
deployment into declaration debt; relaxing it voids published theorems.

**Consensus for grants, local for denials** [D] — the unifying rule, and the sentence the design is
organized around.

---

## 5. The record

**Effects** [P] — exactly {tool invocation, principal emission} (ADR-0015). Exhaustive by claim.

**Authority changes** [P] — exactly {promotion, anchor issuance}. ⟨S6-12⟩ break-glass and erasure
invocations still need a place in one of the two sets.

**The admit decision is the orderable event** [P] — not the emission. **Denials are not ordered:** a
denied effect never crosses the boundary, and absence of effect is not an event. The critical review
(CR-3, CR-7) argues this conflicts with what a correlator needs and with ADR-0020's evidentiary role
for denials, and proposes per-principal sequence numbers on denials.

**The audit chain** [P] — `effect → admit → bundle ⊑ floor → rules epoch → issuance → the intent
axiom`. No link is assumed except the last.

**Effect exclusivity** [P] — the principal reaches the world only through the alphabet. ADR-0015
makes it a **mechanism claim** rather than an assumption — *conditional on the sandbox gap*. Until
ADR-0022 §6 is discharged, CR-1 holds that the claim is no stronger than the assumed version, and
"strictly stronger than Moon & Varshney" is retired wording (§14).

**Round** [A in Run / P in Build] — the unit of topic scope. In Run, a cycle of principal activity
(ADR-0003, Accepted). In Build, **one pipeline invocation** (ADR-0021, Proposed). See §13 for the
collision.

**Topic per principal per round** [A] — one topic per principal per epoch or round, sealed on emit
completion, with per-topic access control, per-use-case retention, explicit replay authorization,
write-time masking by wrapper Rego, and no tiered storage (ADR-0003).

**Seal** [A in Run / P in Build] — the instant a round topic becomes immutable and the erasure unit
becomes well defined. In Build, sealing moves to submission (ADR-0021, Proposed).

**The topic is the unit of erasure** [A] — deleting a sealed container never edits a signature or a
hash chain, and a masking miss has a blast radius of one round. **Cost: topic count, principals ×
rounds** — the critical review's first K finding, against KRaft's metadata churn.

**Control-plane facts vs cognitive payloads** [A] — trace conformance needs actions, identities, and
ordering; forensics needs the text. In the archive the control-plane record keeps a hash and a
pointer, and plaintext lives in a **separately governed store built for deletion** (ADR-0004).

**Erasure** [A] — a **modeled event**: consensus-ordered, modeled in TLA+, recorded in the log it
modifies. Authorization lives in the verified object, not in a bundle. Mechanism: deletion of sealed
topics and of plaintext-store entries.

**Crypto-shredding** [A, rejected] — considered and **rejected** as the primary mechanism: it leaves a
verifying envelope over unreadable ciphertext, a hole no auditor can distinguish from suppression.
⟨S6-11⟩ three documents in the corpus still say the opposite.

**Demand taxonomy** [A] — erasure demand types 1–5 (ADR-0006). **Type 5** ("hide that a record
existed") is *unaddressed* in the accepted text, which entangles it with break-glass and defers it to
ADR-0013. ADR-0028 (**Proposed**) argues it is structurally excluded at the archetype because F6
records the erasure. Do not cite the exclusion as settled.

**Replay** [A] — reconstructs **what crossed the membrane**, not what happened inside it (ADR-0020).
The Observer and replay read the same stream, so an investigator can never be shown something the
Observer lacked at detection time. That is what keeps `L` an honest number.

**Legibility** [P] — the archetype property that replaces immutability: *every admitted boundary event
remains readable by the declared audit authority for the declared horizon.* HIPAA-style regimes
subtract the **record**; SCI-style compartmentation subtracts the **reader set** and is
archetype-conformant except at spill remediation. The archetype log is the maximum projection each
regime derives from.

**Forensic floor** [P] — six classes non-erasable for the declared horizon (ADR-0028): **F1** admit
decisions · **F2** stop attribution (e-stop, lease-expiry eviction, `deny=all`) · **F3** promotion
votes · **F4** anchor issuances, including genesis · **F5** break-glass invocations · **F6** erasure
events themselves. All are control-plane facts; **no cognitive payload is in the floor**. **No new
primitive:** each class is a policy-floor denial on the erasure envelope, so removing a class is a
floor relaxation. Two seams: ⟨S6-5⟩ votes live on erasable round topics, ⟨S6-14⟩ the horizon ends at
re-genesis.

**Stop attribution is a feedback path, not just evidence** [P] — in system-theoretic terms (STPA) the
Observer is a controller, not a probe. That is why F2 is non-erasable.

**Archive** [D] — the system of record (ToO rev 5 §4.2). A 09.16 drafting session concluded it should be
kept **out** of the trusted computing base and made verifiable against the Paxos log rather than trusted;
that is session material, not a record. **[S]**

---

## 6. Detection

**Observer** [A] — the detection layer. Every semantic concern is an Observer finding and every
finding is **deny-only**: a block, a quarantine trigger, or an eviction, never an admit precondition.

**Placement** [A] — Observer replicas never share a device with the Thinker they watch, and no two
replicas share a device. A shared device means shared driver, firmware, memory error domain, thermal
and power events, and host kernel. **A Byzantine quorum of co-resident replicas is arithmetic
fiction.**

**Monoculture** [O] — an Observer should come from a different model family than the agents it
watches. Sharing a family is a shared blind spot. **Two records disagree on whether this is closed.**
ADR-0016 §5 says seat distinctness by lineage "makes the cross-family Observer requirement
enforceable rather than advisory and closes the monoculture open item." ToO rev 5 §5.1 states it as a
bare rule, G1 §9 still lists it as an unwritten declaration, and NIST MANAGE 3.1 is still marked a
gap. CR-10 is the reason to doubt the closure: three seats, two lineages, so two seats must share
one.

**Scoping** [A, reversed in effect] — ADR-0008 was accepted with a shared, orchestrator-level Observer
group. ADR-0023 found neither scoping dominates, and the archetype is now **per-principal Observers
plus a cross-principal correlator**. The accepted text stays in force until a superseding record
exists.

**Cross-principal correlator** [O] — the answer to the strongest published impossibility result
(Shukla & Joshi), and currently **a noun**: no record, no alphabet, no placement rule, no seat, no
statement of what it reads.

**Silence is invisible** [S] — CR-2's name for the detection layer's failure mode: a dead,
partitioned, starved, or colluding Observer produces the same observable as a clean system. The
monotone rule that keeps judgment out of the admit path also makes the absence of judgment
invisible.

**Veto-seat liveness heartbeat** [O] — the proposed fix, admissible under ADR-0007 because *the
Observer replica set attested liveness within the last `T`* is a totally extractable fact rather than
a judgment. Open for promotion only; CR-2 argues it applies to every Run admit.

**Untrusted monitor** [S] — the AI-control term for what the Observer is (a model watching a model).
⟨LP-4⟩ proposes declaring it untrusted and requiring honeypot validation at seat admission.

**LTRO** [D] — **Listener / Thinker / Reader / Observer**, the internal decomposition of an agent
principal, giving separation of duties inside one principal. Human principals are atomic, stated as a
weakness. **⟨LP-1⟩ the LTRO has no decision record**; its seat semantics are scattered across
ADR-0008, ADR-0016 §5, ADR-0018, and ADR-0022.

**Seat** [A] — the binding point for a Persona, and the unit of attestation and attribution. **⟨LP-10⟩
principal ≠ seat:** principal is authority and eviction, seat is attestation and attribution.

**Reader** [A] — the seat that reads logits. May colocate with the Thinker; it was never an
independent fault domain. **⟨LP-12⟩** its white-box role is in tension with seat distinctness (see
CR-10: three seats, two lineages).

**Listener** [D] — **⟨LP-3⟩** proposes it become a deterministic labeling stage with no Persona,
which would make it the only deterministic seat.

**Build has an Observer** [P] — ADR-0021 closes the sharpest contradiction on the board (a hostile
domain with enforcement and no detection) by reusing the round-topic scheme. **Detection is cheaper
in Build**, because the promotion gate blocks and detection only has to finish before the gate
clears — which makes its absence harder to defend.

**Decode observability** [A] — narrow by decision (ADR-0019). `none` is the only unconditional value;
`topk_logprobs` is admissible for decoding conformance and substitution detection only, **never** for
claims about `L`.

---

## 7. The model is pinned

**Persona** [A] — *the model enters the system as a Persona*: a signed, versioned Build artifact
binding a model to its complete runtime configuration. Eleven fields at minimum (ADR-0016 §1):
provenance/lineage · Persona ID · sequence number · system prompt · decoding parameters · **decoding
stack version** (identical weights under a different sampler is a different Persona) · determinism
class · **context window and truncation policy** (an unpinned truncation rule silently changes what
the Thinker saw) · decoder identity and hash · decode-observability class · seat binding. Stronger
than the OpenSSF Model Signing specification, which signs the model artifact alone.

**Verification versus suitability** [A] — kept apart throughout ADR-0016, because fusing them reads as
a retreat from the thesis. **Verification** (signature, hash, provenance-chain integrity, record
completeness) is decidable and is a legitimate precondition of admission. **Suitability**
(evaluations, benchmarks, red-team findings) is evidence, never a precondition. *TOPAK verifies
Personas; it does not verify models.*

**Evaluation is deny-only** [A] — ADR-0007 applied to a new artifact class: a passing evaluation can
never admit a Persona; a failing one can deny or quarantine it. The asymmetry is what makes the
weakness of evals harmless.

**Provenance degradation** [A] — where the artifact is not in hand the gate does not soften; the rung
changes: **verified** (artifact possessed, hash-checked) → **attested** (provider signs a statement) →
**asserted** (a version string and nothing else).

**Persona proliferation** [A] — every parameter change is a new Persona and a new promotion;
temperature becomes a deploy-cadence change. Stated in the record as the correct price. The floor
bounds Persona *classes*, so the registry grows without the admission logic growing.

**Persona revocation is an ordinary deny** [A] — local, no consensus, no floor exception, and
explicitly **does not add to ADR-0013's carve-out count**.

**Lineage** [A] — a Persona's training provenance. The archetype admits only **in-house pre-trained
Personas from two independent lineages**. Overlapping public corpora do not count as independent.

**Seat distinctness** [A] — the Observer's Persona must differ from the Thinker's **by lineage**, not
merely by configuration, expressed as a policy predicate over Persona provenance.

**Independent-lineage criterion** [O] — unwritten; ADR-0017 owes a **decidable or auditable**
criterion for lineage independence. Until it
exists, the archetype's `Contained` set is unreachable on this axis as well as on the sandbox axis.

**Typed lift split** [A] — the model-specific **decoder** ships in the Persona; the model-agnostic
**validator** lives in the mechanism (ADR-0018). The ADR-0010 move — verified core, parameterized
edge — applied to syntax.

**Silent substitution** [D] — a provider updates weights, rotates a tokenizer, or deprecates an
endpoint: the pin breaks with **no event anywhere in the system**. Boundary B8, the largest empty
cell in the register. Havoc semantics make a *worse* model harmless for containment; what changes is
that substitution becomes a detectable identity mismatch instead of an unmodeled event.

**No staleness argument for Personas** [D] — a stale bundle is safe because the floor bounds it below.
**Nothing makes an out-of-date Persona monotonically less dangerous.** Readers will assume the floor
argument generalizes; state that it does not.

---

## 8. Time, intervals, boundaries

**Boundary register** [D] — the companion document listing fourteen boundaries, each with its
cadence, instant, interval of untruth, and behavior when unavailable. Read it **by its holes**.

**Cadence** [D] — the rate at which artifacts on each side of a boundary change. A cadence mismatch is
what forces a boundary to exist.

**Instant** [D] — the moment two independently evolving artifacts are pinned against each other and a
check becomes decidable. **A boundary with no instant has no enforcement point.** The four instants
are **promotion**, **seal**, **fence**, and **revoke** — the last with semantics undefined.

**Interval of untruth** [D] — the window during which a boundary's claim is untrue or not yet known to
be true. An unbounded interval with no monotonicity argument is an open hole.

**Epoch fencing** [A] — after an epoch increment, actions carrying the prior epoch are rejected by
**mechanism** rather than by policy. The cheapest check in the system, and the only place a temporal
condition is enforced without a policy lookup.

**Lease** [A/D] — the authority object a principal holds: identity, alphabet, topic, epoch, expiry.
Grant is a consensus decision; expiry is a local clock read.

**Lease attenuation** [S] — proposed 09.17: `leaseₙ₊₁ ⊑ leaseₙ` within an epoch. A renewal may narrow
the alphabet, tool allowlist, or topic scope; any widening needs a fresh grant at a new epoch. The
consequence is that **a stale lease becomes monotone-safe**, which makes the lease the second interval
in the register to be solved by monotonicity rather than by bounding, and takes the clock off the
safety path.

**Lease rank** [S] — the proposed lexicographic tuple `(rules epoch, lease epoch, renewal counter)`.
Attenuation bumps the last component; widening bumps a higher one. One check covers both axes.

**Fence token** [S] — proposed: the grant's Paxos log index, rather than a second counter.
Monotonicity must live in the **acceptor** (a durable highest-seen register per principal), not in the
token.

**E-stop taxonomy** [D] — three kinds:

| Kind | Trigger | Authority | Latency | Needs availability |
|---|---|---|---|---|
| **Passive** | Lease non-refresh | Subtracts | ≤ remaining TTL | No |
| **Active** | Unilateral human stop | Subtracts | Decision + `W` | Yes |
| **Break-glass** | Quorum | **Adds** | Consensus round | Yes |

**Quiesce semantics** [O] — stop-admitting is not stop-effecting. A tool invocation already admitted
and handed to an executor is outside the stop. **No quiesce semantics exist anywhere in the corpus.**

**`W`** [D] — the effect propagation window, about a second. **Guaranteed by mechanism.**

**`L`** [D] — Observer detection latency. **An emergent property of a component**, and **unmeasured**,
though the safety argument invokes it.

**`D`** [D] — the human response budget. **An organizational commitment**, named and never budgeted.

**`W < L < D`** [D/O] — the timing chain. The three terms are of **three different kinds**, which is
why forcing them into one classification (specification invariant versus deployment obligation) was
rejected as a false dichotomy. Only partly expressible in standard TLA+. The property that matters may
be a **sum measured against time-to-irreversibility**, not an ordering. **Letter drift is a live
citation hazard** — see §13.

**Clock model** [O] — unstated. What the 09.17 session found when it was finally opened: safety is
clock-free and carried by the fence, so clocks buy **liveness only**; causality (ADR-0005's vector
clock) bounds no interval; intervals whose failure **subtracts** authority can use a cheap local
monotonic clock, while intervals whose failure **adds or preserves** authority need trusted time; and
**no safety decision reads a clock supplied by a principal.** A three-clause record was offered and
not taken up.

**Asymmetric margin** [S] — the holder self-expires at `TTL − δ`; the grantor waits `TTL + δ` before
re-granting. No overlap without trusted time (Chubby's lock delay).

**HITL / HOTL / HOOTL** [D] — human-in-the-loop, human-on-the-loop, human-out-of-the-loop, defined by
**enabling condition**: enabling, disabling only, no channel expressible. Placement is forced by the
consistency budget, not by preference: Build affords HITL; Run's ~1s window leaves HOTL. All three are
`ENABLED` predicates in TLA+.

**HOTL proceeds by default** [D] — disabling only. Combined with deny-only findings and veto-seat
silence, this is the structural half of CR-2.

---

## 9. Deployment variation

**Archetype** [P] — the unique maximum of the parameter lattice. A **reference point, not a shippable
configuration**. **Nobody ships the archetype**, and the TLA+ theorems are proved about an unshipped
configuration — honest only if the declaration records are actually written. ISO 26262's **safety
element out of context (SEooC)** is the stated precedent.

**Degeneracy** [P] — a form obtained by driving named parameters of the archetype to limiting values.
*Degenerate* is the formal register; *reduced* is the operational one. **The effect is premise loss,
not weakening:** theorems are present or absent.

**Admission test** [P] — a variation is a rung only if it is reachable from the archetype by parameter
limit. If it has a capability the archetype lacks, **the archetype is incomplete**, and the rejection
is a finding about the archetype.

**Rung** [P] — a position on one axis. **Rungs are per-axis**; a deployment is a tuple and unqualified
"rung demotion" is barred. See §13 for the collision with attestation rungs.

**Declaration record** [P] — the fixed schema every degeneracy carries: parameter, archetype value,
deployed value, premises falsified, theorems voided, mitigation, and a composition note. **Declaration
is mandatory and mitigation is not; the composition note is mandatory above one parameter.** Existing
records are A-0025, D-0025-1, D-0025-2 (anchor recoverability) and D-0024-1, D-0024-2 (approver fault
tolerance).

**Axes named so far** [P] — Persona provenance, event-log legibility, Observer scoping, effect-stream
role, arguably HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability. **The set is
not enumerated and finiteness of each chain is unproven.**

**Two kinds of degeneracy** [P] — **a promotion degeneracy is a mechanism release; a custody degeneracy
is a declaration.** The first changes what the mechanism admits and reopens a theorem; the second
instantiates the opaque `Authentic` outside the model and reopens nothing.

**Type change** [P] — a degeneracy can move a participant from the gate to principal (or back), which
**moves the trusted computing base**. Admission must check for this, not only for voided theorems.

**Dominance rule** [P] — the archetype moves on a paired axis only to Pareto-dominating values. The
critical review (§2.8) argues the cost function must include **forced authority events** such as
re-genesis, which would put A-0025 itself back under examination.

**Non-increasing TCB** [P] — across archetype versions. Moving a property into *assumed* needs its own
record.

**Composition** [O] — not assumed monotone: two degeneracies may void more than the union of their
theorem sets. Every real deployment has at least three. Until a composition rule exists, **no shipped
deployment can compute its theorem inventory from its declarations.**

**Reversals in effect** [P] — an accepted record whose text stands while a later record contradicts it
in substance. Two exist: ADR-0008's scoping and ADR-0017's ordering-primacy clause, both by ADR-0023.
Both happened within 48 hours, by the author alone, during genesis.

---

## 10. Corpus, process, and verification vocabulary

**ADR** [A] — Architecture Decision Record, in Nygard form, with explicit status and debt tracking. **No
renumbering; tombstones instead** (ADR-0011 is one). **Decomposition test:** a clause that can be
superseded alone is a separate decision.

**Reserved** [C] — a number assigned with no record (ADR-0014). Explicitly a checkpoint label, not a
status class: no file, no digest, cannot be ratified (G-C3).

**Genesis** [A] — the current process, **not a degeneracy**: before the anchor exists there is no
archetype custody to degenerate from. Genesis custody is declared: Scott, sole custodian, (1, 0).
Everything ratified in genesis is trusted by declaration and becomes part of the **genesis TCB**.

**Unilateral ratification** [A] — the custodian may ratify any record with decision text. A record
without decision text cannot be ratified.

**Confirmation-required** [A] — a marker on a ratified record that carries a proof obligation over
privileged paths (**C1**), an exhaustiveness or confinement claim (**C2**), a reversal in effect
(**C3**), or resolves a debt owed by one (**C4**). Until confirmed, a publication citing such a
guarantee says **"author-ratified."** CR-5 proposes a **C5: load-bearing premise**, on the grounds that
the criteria reach the forensic floor but not ADR-0007 or ADR-0010.

**Bootstrap set** [A] — ADR-0024 to 0027. **Cannot be confirmation-required**, because confirmation runs
under those rules and confirming them under themselves would be circular. Its weakest point, stated in
the corpus: **the bootstrap set gets no independent review, ever.**

**Bootstrap trigger** [A] — the anchor may bootstrap once a drafted TLA+ bootstrap specification exists:
five modules (`Genesis`, `Anchor`, `RulesFloor`, `Promotion`, `BreakGlass`), five invariants, and a
mutation for each that must fail. `RulesFloorNV` is a **precursor, not a substitute**.

**Genesis bundle** [A] — assembled at the ceremony: the corpus manifest including the confirmation-required
set, the specification digest marked checked or drafted-only, and the genesis rules. Every key-holder
signs its digest; that is issuance epoch 0. **The only artifact never promoted.**

**Re-genesis** [P] — the exit from a frozen rules set. Creates a **successor system**, and is the largest
authority event the design has, performed under duress and producing a new TCB.

**Genesis debt ledger** [A] — the per-checkpoint tally of the confirmation set. **No forcing function**,
by decision: the debt is visible, not bounded. At G1: 2 ratified confirmation-required, +4 on queue C,
+3 when written, total 9.

**G checkpoint** [C] — a genesis checkpoint. **G1** (2026.09.15) is the corpus's state of record and is
**immutable once cut**; corrections go into G2. Each ratified batch cuts the next one.

**Theory of Operation** [D] — the narrative checkpoint. **Not the state of record** since G1; it explains
how the design fits together, and status words appear only where status changes the meaning.

**Readiness key** [C] — G1 §2: **R** ratifiable now · **R·CR** ratifiable, confirmation required ·
**N** not ratifiable (no decision text) · **BS** bootstrap set · **—** already accepted, or tombstone.

**Ratification queue** [C] — batches in dependency order: **B** bootstrap core · **C** confirmation
required · **D** plain · **E** errata · **F** needs text before it can be queued. (The queue letter
**C** and the confirmation criterion **C1–C4** are different alphabets that happen to meet here.)

**Finding tags** [D/C] — six families are in use, and all are still live:

| Tag | Source | What it marks |
|---|---|---|
| ⟨S6-n⟩ | Narrative log 09.15 | Records that disagree, found during the ToO rev 5 pass (S6-1…S6-18) |
| **CR-n** | Critical review 09.16 | External-facing findings (CR-1…CR-20) |
| **N17-n** | Narrative log 09.17 | What the three deferred items exposed when opened (N17-1…N17-3) |
| ⟨LP-n⟩ | LTRO field assessment 09.16 | Seat and delegation findings (LP-1…LP-13). **Session material; the assessment is not a Project doc**, so these numbers are not checkable against the corpus |
| T2-n, T3-n, S3-n, S4-n | Cleanup steps 2–4 | Recovery, fold, and normalization findings; dispositions in G1 §6. S3-2 and S3-4 are still **Open**, in queue F |
| G1-n | The G1 cut | G1-1 applied at the cut; G1-2 still **Open**, same site as S3-4 |

**Custodian call** [C] — a decision applied during cleanup and marked reversible; confirmed by the next
cut (G-C5). N-1, N-2, and N-3 were confirmed by G1.

**Havoc oracle / havoc semantics** [A] — modeling an agent as capable of anything its alphabet allows.
The construction the whole design runs on, reached independently from a distributed-systems starting
point and concordant with Moon & Varshney's Theorem 3.2.

**Non-vacuity witness** [P] — a reachability result showing a property is not discharged over nothing.
`RulesFloorNV` is the corpus's one checked artifact and the shape every other gate should take. **No
non-vacuity gate exists for TLA+ invariants**, which mirrors the Rego vacuity problem one layer down.

**Mutation** [P] — a deliberately broken variant of a specification that **must** fail the check. "Every
invariant ships with a mutation that must fail" is the corpus's discipline, and is still rare in the
field.

**TLC vs TLAPS** [O] — undeclared (NIST MAP 2.3). TLC over bounded constants gives non-vacuity and
discrimination, **not proof**. The easiest thing in the corpus for a formal-methods reviewer to attack.

**Trace conformance** [D] — checking a recorded execution against the specification. It appears in
ADR-0004's Context ("operates over the abstract state machine"), not in its Decision, so it is an
obligation the corpus assumes rather than a decision it has taken. Currently the closest thing to a
refinement from specification to implementation (ADR-0005 Consequences; CR-4).

**Refinement** [D] — used in two distinct senses: `bundle ⊑ floor` (policy), and specification-to-
implementation refinement (formal methods). The corpus has the first and **does not have the second**
(CR-4).

**Trusted computing base (TCB)** [O] — never enumerated. The 09.17 session proposed a three-column shape:
**trusted** (about six obligations per item: measurement, minimum version, re-attestation trigger,
residual, assumption of use, gate check), **explicitly not trusted** (the long column, and the asset),
and **residual / out of scope** (each with the rung that would buy it down). Plus a **derivation rule** —
every `CONSTANT`, `ASSUME`, unrefined module, environment step, and floor entry is an entry — so the
list regenerates per archetype version instead of being re-authored. "Zero assumptions" fails twice:
mechanically it relocates, and formally it hits the intent axiom. **The product of the hard path is a
monotone discharge ledger, not an empty list.**

**Guaranteed / measured / declared** [S] — the decomposition shape that keeps recurring: in `W`/`L`/`D`,
in the TCB's three bins, approximately in the attestation rungs, and earlier in ADR-0025's three-way
split of "infallible."

---

## 11. Outstanding — terms that name a hole

Each of these is a vocabulary entry the corpus uses as if it denoted a mechanism. Each is on the open
list (G1 §9) or arrived since.

**Sandbox gap** [O] — the set of unnamed effects. Blocks ADR-0022 §6 and ADR-0015's exhaustiveness, and
decides whether `Contained` has members. **No mechanism, no owner.** Sandboxing is commodity in 2026, so
this is an integration, declaration, and attestation task, not a research gap.

**Container vacuity** [O] — the same hole named from the predicate's side: `Contained` may currently have
**no members at all**, on two axes (confinement and lineage independence).

**Confinement rungs** [S] — the ordering proposed 09.17, by attestation strength: **rung 0** none
declared · **rung 1** asserted by the launcher · **rung 2** measured boot · **rung 3** confidential VM
with an independent verifier. Unrecorded. The minimal solution — rung 1 alone — was sized at one record
plus one model-checking run.

**Mechanism versus instant** [S] — the sharp form of the sandbox gap: the mechanisms are commodity; the
hard part is **the moment `Contain` knows it is running inside the mechanism it assumed**. That instant
is boundary B12's empty cell, and **lease grant can be borrowed for it** — no new boundary needed.

**Contested** [S] — Sokolov's third attestation verdict: signature valid, measurements diverge. TOPAK has
**no vocabulary for evidence-of-discrepancy versus absence-of-evidence**, and rung 1 has no way to
produce one.

**Lease schema** [S] — the record all three deferred items converge on: the clock reaches it (expiry on a
local monotonic clock with an asymmetric margin), container vacuity reaches it (the lease binds the
confinement-profile digest), the TCB reaches it (the lease's field list is the enumeration, serialized),
and the identity gaps reach it from a fourth direction. **The likeliest next record.**

**Delegation / on-behalf-of** [O] — ⟨LP-8⟩. No record for delegation, on-behalf-of attribution, or the
provenance of a task that passed through three principals. `W < L < D` has **no chain-depth term**, against
published results showing asynchronous detection decays factorially with chain length.

**Flow** [O] — CR-6. A per-action syntactic envelope cannot say "data read from X may not reach sink Y."
The proposed fix is inside ADR-0007, not against it: **source labels as syntactic-lift fields**, since
provenance is mechanically extracted and is not meaning. The 09.17 session added the cost boundary:
self-prefix path rules stay in EL zone 1, while cross-principal flow needs a global ordered view where a
stale prefix **fails open systematically**, which disqualifies it from the admit path and assigns it to the
Observer.

**Observer quarantine gate** [O] — modeled event or internal step. Unblocks ADR-0005 and may eliminate the
vector clock. "The cheapest open question on the board" since 09.12.

**Floor authorship** [O] — ADR-0014, Reserved. Narrowed to proposal eligibility; still the natural home for
`Invoke` hermeticity and floor fitness. **Reserving the number while the two gates it would own stay
unowned is the corpus's most expensive deferral.**

**Signed message format** [O] — protobuf versus canonical CBOR. Genesis-blocking: the genesis bundle needs
it.

**Assumptions of use** [O] — the SEooC-shaped declaration the register calls the highest-leverage fix:
putting them at the front converts the largest weaknesses from omissions into declared conformance.

**Residual risk statement** [O] — NIST MANAGE 1.4, headed by anchor capture.

**Reversibility index** [X] — cited by the feature list (F5.5) and the boundary register (§7.2) as
ADR-0007's; **it does not appear in ADR-0007's recovered text**. A dangling concept with no home, and the
mechanism ADR-0009's irreversible-domain clause would need. Belongs with G1 §10's unrecorded
DAG-reversibility decision.

**Army of one** [X] — a degraded mode stated as a decision in session and never filed (G1 §10, session
`a7fad171`). The answer to NIST GOVERN 6.2, third-party failure contingency.

---

## 12. Adjacent — vocabulary readers arrive with

Terms TOPAK does not own but must either claim, disclaim, or position against.

**Distributed systems.** PACELC · PC/EC · PA/EL · **EL zones** (zone 1 enforcement, zone 2 leases, zone 3
the effect stream) · linearizability · CALM · Paxos, Multi-Paxos, Byzantine fault tolerance, crash fault
tolerance · KRaft · `acks=all` · vector clock · fencing token · lease (Gray & Cheriton) · quorum ·
split-brain.

**Safety and supply chain.** SEooC (ISO 26262) · STPA · trusting trust · SLSA and in-toto · reproducible
builds · The Update Framework (TUF) · Certificate Transparency and Sigstore Rekor · RFC 9334 (RATS) and
its three freshness models — nonce, **epoch ID**, timestamp · measured boot · confidential VM · OpenSSF
Model Signing · SPIFFE/SVID and IETF WIMSE · macaroons and biscuit tokens (attenuation-only credentials).

**Formal methods.** TLA+, TLC, TLAPS · `ENABLED` · `INSTANCE` · invariant, safety, liveness · refinement ·
vacuity detection (Beer et al.) · Dafny, Verus, Lean · SMT · enforceable security policies (Schneider
2000; Basin, Klaedtke & Zălinescu 2013) · the de Bruijn criterion and `#print axioms`.

**The field's counterparts.** Moon & Varshney (containment verification; the parent result) · AgentFlow
(flow-centric policy; "the policy author and runtime are trusted") · CaMeL and FIDES (capabilities and
information-flow control) · Cedar and Cedar Analysis (Lean-verified semantics, decidable permissiveness) ·
Microsoft Agent Governance Toolkit (same process boundary; trust scoring) · Confluent's Agent Decision
Record on an immutable hash-chained log · AI control (Greenblatt; Nelson; Makins; Arike) · Shukla & Joshi's
impossibility results · Aegis (proof-of-enforcement, to be distinguished from verified-enforcement-mechanism).

**Regulatory and framework.** NIST AI RMF and its Playbook (GOVERN / MAP / MEASURE / MANAGE) · OWASP Agentic
Security Initiative Top 10 · HIPAA · SCI compartmentation · GDPR right to erasure — which, per CR-11, applies
to the human identifiers the forensic floor retains, so each class needs a legal-basis line.

**Worked examples in use.** The 767 case (authority gradient, detection lag, a human inside the loop) as the
lede · the scientific method as a containment analogue · **the seatbelt, deliberately not the lede** —
it maps to assumptions of use and to the 1974 interlock, but a belt is mitigation while `Contain` is
admission, and invoking it summons risk compensation.

---

## 13. Terminology hazards

Live collisions. Each needs a ruling before publication; the first three are new since the last glossary.

1. **"Rung" — two unrelated orderings.** ADR-0023's per-axis degeneracy rungs, and the 09.17 confinement
   attestation rungs 0–3. Both appear in the same sentence in current sessions. **Rename one.** (Note that
   a confinement *upgrade* is a subtraction of effect surface, so the two orderings even run in opposite
   directions.)
2. **"Floor" — now four things.** Policy floor, rules floor, forensic floor, and floor *fitness*. Plus
   `bundle ⊑ floor` and "floor minimum" (a seat count). The word is doing more work than it can carry.
3. **"G1" — checkpoint versus gate.** Genesis Checkpoint G1 and G2, against the three gates called
   G1–G3 in review material. Also G1-1, a finding tag from the cut itself. **Name the gates; don't
   letter them.**
4. **"Agent" — three referents.** The A in TOPAK, the LLM inside a seat, and the OPA daemon (Open Policy
   *Agent*). The article uses all three. Worst offender, and unresolved since 09.11.
5. **"EL" — PACELC's else-latency, read as "eventually linearizable" on sight** by distributed-systems
   readers. Either expand it every time or relabel the zones.
6. **"Round" — Build and Run mean different things.** A Build round is one pipeline invocation; a Run round
   is sub-second to seconds. Retention horizons diverge accordingly. Always qualify.
7. **"Epoch" — four counters.** Rules epoch, anchor epoch, lease epoch, deployment epoch. The lease-rank
   proposal orders three of them lexicographically, which is exactly the point at which the ambiguity stops
   being harmless.
8. **`L` and `D` letter drift.** Before 09.12, `L` was lease duration and `D` was detection lag. From 09.12,
   `L` is Observer detection latency and `D` is the human response budget. **Any citation of `W < L < D` to
   pre-09.12 material is wrong in substance**, and the justification for `W < L` differs under the two
   readings.
9. **"Consensus" — control plane, not agents.** Paxos orders orchestrator decisions *about* agents. It is not
   consensus *among* agents over their outputs, which is a different literature TOPAK deliberately does not
   join.
10. **"Declared" — three uses.** A declaration record (ADR-0023), the declared bin of the TCB, and declared
    custody (ADR-0025). Related by shape, not identical.
11. **"Byzantine" — agents, not orchestrators.** Rev 5 uses it of agents while the control plane runs
    crash-fault-tolerant Paxos among implicitly trusted orchestrator nodes. **The control plane's fault model
    is never declared.**
12. **"Proved" and "theorem."** The corpus's register throughout, against one checked 30-line model. CR-4's
    recommendation is to say **"obligations stated as theorems, with mutations"** and never "proved" in the
    present tense.
13. **"Degenerate" — two problems, one of them assigned here.** ADR-0023's Consequences hands this
    document an explicit obligation: **note the collision with TLA+'s own "degenerate behavior."**
    Separately, the word reads pejoratively outside the formal register, which the *degenerate* /
    *reduced* split in clause 1 is meant to mitigate. Both belong in the article's first use.
14. **Domains versus components.** `Build`/`Run`/`Contain` against T/O/P/A/K. Two axes; T appears in both
    domains and K spans them. **The component × domain mapping table is still unwritten** — it has been on the
    open list since 09.11 and it is the thing that kills this confusion outright.

---

## 14. Retired wording

The 09.11 glossary went stale because vocabulary moved and nothing tracked the movement. This section is the
countermeasure. Each line is wording that appears in corpus documents and should not be repeated.

| Retired | Replacement | Authority |
|---|---|---|
| CI, Orch | `Build`, `Run` | ADR-0001 |
| Three TLA+ spec domains | Two domains, one component instantiated twice | ADR-0002 |
| "Semantic containment" | Boundary-enforceable containment | ToO rev 5 §2.1 |
| Deployment ladder / profiles | Degeneracy; per-axis rungs; a deployment is a tuple | ADR-0023 |
| "Immutable" log | Legibility | ADR-0028 |
| Crypto-shredding as the erasure mechanism | Sealed round-topic deletion plus plaintext-store deletion | ADR-0003 (the rejection), ADR-0006 with ADR-0004 (the mechanism) ⟨S6-11⟩ |
| Kafka as ordering authority or system of record | Transport with a durability window; Paxos orders, the archive records | ADR-0005 |
| "Strictly stronger than Moon & Varshney" | "Conditional on confinement (ADR-0022 §6)" | CR-1 |
| `D` as detection lag; `L` as lease duration | `L` detection latency, `D` human response budget | 09.12 onward |
| Moon & Varshney §4.2 | §4.6 and Appendix B | ADR-0002 E1 |
| ADR-0016 §8 (in ADR-0018, ADR-0019) | ADR-0020 | Errata queue E |
| Promotion on a human signing key | A quorum grant read from issued rules | ADR-0024 |
| "The floor is the one artifact verified rather than promoted" | The floor is verified with the mechanism; the release carrying it is promoted. Only the genesis bundle is never promoted | ToO rev 5 §3.2 ⟨S6-16⟩ |
| "Varshnay" and other misspellings | **Varshney** | ToO rev 5 §11.1 |
| "Cheap to close" (of the clock model) | Carried across three checkpoints; retired as a label | N17 §5 |

---

## Sources

**Corpus.** Theory of Operation rev 5 (2026.09.15) · Genesis Checkpoint G1 (2026.09.15) · boundary register
(2026.09.13) · feature list (2026.09.15 rev 1) · ADR-0001 to ADR-0029 at their G1 digests · `RulesFloorNV.tla`
and its TLC results.

**Derived, not records.** Critical review (2026.09.16, CR-1 to CR-20) · narrative log (2026.09.17, N17-1 to
N17-3) · narrative log (2026.09.15, S6-1 to S6-18). The **LTRO principal field assessment** (2026.09.16,
LP-1 to LP-13) is cited from session history and is **not in the Project or the corpus**; its findings are
reported here as session material and its numbering is not independently checkable.

**Unrecorded session material**, marked **[S]** above and drawn from 09.16–09.17: container vacuity (rungs,
the borrowed instant, *Contested*) · clock and `W < L < D` · TCB enumeration (three columns, derivation rule,
discharge ledger) · lease implementation (attenuation, rank tuple, fence token) · flow and AgentFlow (CR-6's
cost boundary).

**External.** Moon, R. & Varshney, L. R., *Containment Verification: AI Safety Guarantees Independent of
Alignment*, arXiv:2605.09045v2 · Sokolov, arXiv:2608.00801 (attestation verdicts) · the counterpart set listed
in the critical review §3 · NIST AI RMF Playbook.
