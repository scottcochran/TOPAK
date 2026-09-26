# TOPAK — Glossary

**2026.09.26** · derived · regenerated from scratch · DRAFT

**Basis.** Genesis Checkpoint G3 (2026.09.25) and Theory of Operation revision 7 (2026.09.25), with the record files
they cite. Where the two disagree, G3 wins. Two records written after the G3 cut, ADR-0034 and ADR-0035, are both
Proposed. They appear only in §10, and they are marked there.

**What this supersedes.** The 2026.09.17 glossary, which was cut against rev 5 and G1 and now predates two
checkpoints (G3 open item 12). Nothing from it is carried over unchecked. Its session vocabulary **[S]** has either
reached a record, and appears here under that record, or is dropped. §14 lists the moves.

**This document decides nothing.** It reports what the terms mean in the corpus as it stands, including where two
sources disagree.

---

## 0. How to read

| Tag | Meaning |
|---|---|
| **[A]** | Defined by an Accepted (genesis) record |
| **[A·CR]** | Defined by an Accepted record, or amendment, marked confirmation-required. Cite as *author-ratified* |
| **[P]** | Defined by a Proposed record, a pending amendment, or a DRAFT artifact. The wording can still move |
| **[D]** | Derived: used in the narrative, with no record of its own |
| **[C]** | Checkpoint convention, fixed by G1–G3 |
| **[R]** | The reference implementation (ADR-0033). It is evidence, not the verified object |
| **[O]** | Outstanding: the term names a hole rather than a mechanism. Numbers refer to the G3 §7 open list |

Record status is G3 §1 and is not restated here except where the status changes what a term means.

---

## 1. The pattern

**TOPAK** [A/D]: an architecture pattern for autonomous multi-agent collaboration that is safe by design. The
letters name **roles, not products** (ADR-0030 §2, ADR-0033 §2). Each role carries a stated obligation, and any
instrument that meets it may be substituted.

| Letter | Role | Instrument at the reference |
|---|---|---|
| **T** | Formal specification and model checking | TLA+, TLC |
| **O** | Policy as code: a verified floor evaluator and a per-request bundle engine | Cedar (floor), OPA and Rego (bundle) |
| **P** | Consensus over the control plane | Sans-IO Multi-Paxos |
| **A** | The principals doing the work | Agents, reached through MCP |
| **K** | Event transport | Kafka |

**The premise** [A]: *an agent is Byzantine at every deployment position.* Safety never depends on what a model
means or intends, and models stay out of the TCB (ADR-0007).

**The inversion** [D]: the Byzantine threat lives in **Build**, not Run, because Build principals author the
specifications, policy and floors that Run is judged against.

**Safe by design** [D]: the project's descriptor. It means *containment checked about the mechanism*. It never means
*safe outputs*.

---

## 2. Domains, principals, the membrane

**`Build`** · **`Run`** [A]: the domain that produces artifacts, and the domain that operates them (ADR-0001).

**`Contain`** [A]: the containment component. It is one component instantiated twice, not a third domain.

**`Build(Contain) → Run(Contain)`** [A]: the structure. The arrow is authority flow. The parentheses are a
refinement boundary: specification conjunction plus existential hiding (ADR-0001, ADR-0002). The notation does not
survive being spoken, so prose has to carry the nesting.

**Boundary-enforceable containment** [A]: what `Contain` claims. It has two conjuncts: a **checked** property class
over the alphabet and its envelope, and **assumed, operationally discharged** effect exclusivity.

**Principal** [A]: *anything evictable by an authority other than itself.* Principals are inside the proofs.

**At the gate** [A]: whatever is not evictable. It sits outside the proofs and is carried as an assumption or a
declaration. **Resignation is not eviction** (ADR-0002 A2). At archetype custody the anchor key-holders are at the
gate. At degenerate custody they become principals, which is a type change (§8).

**`Contained(p)`** / **`Mediated(p)`** [A/D]: a principal that reaches the world only through its alphabet, and one
with some effect path that no action names (a shell, egress, a git remote). Safety theorems quantify over `Contained`
principals. `Mediated` principals get attribution and authorization, not containment. **Rung 0 is `Mediated`,
always.** A higher confinement rung is necessary for `Contained` but not sufficient, because the provenance axis
must also clear. **`Contained` is unreachable at every rung today.**

**Weakest-link provenance** [D]: a candidate with no record number. A provenance chain that contains a `Mediated`
principal yields attribution, not a safety property.

**Action alphabet** [A]: the finite, typed vocabulary of a principal's effects.

**Build alphabet** [A, except §6]: **egress only**, six variants: `Read(ref)` · `Draft(target, content)` ·
`Invoke(tool, inputs)` · `Emit(record)` · `Submit(digest | ⊥)` · `Vote(verdict, digest, evidence, rulesEpoch)`.
Every action carries an epoch and a lease. There are three mechanism parameters: corpus root, tool allowlist and
round bound (ADR-0022).

**Run's alphabet** [O, 13]: no record defines it. `RunInvoke` and `RunEmit` are provisional in the floor and at the
reference.

**Finite in variants, not in instances** [A]: the floor is analysed per action variant over schema S with symbolic
parameters. It is not analysed by enumeration.

**Seat separation** [A]: for each artifact, the author and the voters are disjoint. A voter cannot `Draft`, `Invoke`
or `Submit`.

**Confinement obligation** [O, 1]: ADR-0022 §6. No shell, no egress, no filesystem outside the workspace and corpus,
and no path to the artifactory except `Submit`. §6 is the one section of ADR-0022 that is **not ratified**. The gap
it leaves is the **sandbox gap**.

**`Invoke` hermeticity** [O]: the per-allowlist-entry obligation that a tool opens no unnamed effect path. **One
allowlisted tool with a socket collapses the envelope to vacuity.** It is assumption of use A2, and it has no owner.

**Capability cost** [D]: no shell, no package installation, no network and no git. This is not how agents write code
today, and the article has to say so first.

**Front door** [R]: the reference exposes the six variants as MCP tools and nothing else. That makes the alphabet
the whole **protocol**, not the whole **channel**: an agent with a shell never has to ask.

---

## 3. The lease

**Lease** [A·CR]: **one composite credential, granted for one round, with a closed schema** of twelve fields:
principal, seat, Persona, epoch, fence, rules epoch, bundle, confinement, alphabet, round, role and TTL (ADR-0031).
A capability that is not a field is not carried.

**One live lease** [A·CR]: a principal holds at most one live lease, and a grant requires that none is live. Without
this rule, monotone renewal guarantees nothing.

**Round-coterminous** [A·CR]: a lease lives exactly as long as its round.

**Fence** [A·CR]: the Paxos log index at grant. Leases, admits and issuances are ordered by one log.

**Renewal only narrows** [A·CR]: a renewal may narrow the alphabet, lower the rung or shorten the TTL. It keeps the
bundle, the round and the role, because none of the three is ordered, so changing any of them needs a grant. So
**tightening a live round ends it.**

**Targeted revocation** [A·CR]: ends the leases that match a principal, a Persona or a confinement profile, bars
later grants to it, and lapses the seat's break-glass approvals. That last effect is the C1 marker. Nothing else
stops.

**Epoch fence** [A]: ends every live round. It is kept for e-stop and for scopes nobody can name. After an epoch
increment, prior-epoch actions are rejected by the mechanism, not by policy.

**Revocation is permanent within the chain** [A·CR]. **Lifting a revocation** [O, 22] adds authority, and no record
says who may do it.

**Expiry is local, then ordered** [A·CR]: a replica reads its own monotonic clock with a margin that errs early. The
first replica to see expiry proposes the round's end as a log entry (ADR-0031 E1).

**Per-round TCB** [A·CR]: the field list. Persona, confinement, bundle, alphabet, round and role are checked at grant
and assumed for the round. Epoch, fence and rules epoch are compared on every action.

---

## 4. Policy and the floors

**Syntactic lift** [A]: mechanical, total extraction of a field from a constrained call interface. It is the only
way a field may enter the admit path.

**Semantic lift** [A]: a model's judgment entering the admit path. It is **prohibited** (ADR-0007). A classifier's
output enters only as an Observer finding, and findings subtract authority.

**Verified object** [A]: the enforcement mechanism, its version pinning, its epoch fencing, a minimal policy floor
and a minimal rules floor (ADR-0010, A1). Everything else is a versioned parameter.

**Policy floor** [A·CR]: the minimal, default-deny floor inside the verified object. Containment is checked against
it.

**Composition** [A·CR]: **admit ⟺ floor_permit ∧ ¬bundle_deny**, over one frozen input (ADR-0030 §1).
`floor_permit` requires Allow **with no evaluation error**. `bundle_deny` holds unless the bundle affirmatively
allows, so a deny, an error, an undefined result, an absent bundle and an unreachable bundle all refuse. **A bundle
is never asked whether to grant.**

**`bundle ⊑ floor`** [A·CR]: now a **property of composition**, not of the bundle. It holds for every bundle at every
age, so nobody decides it at promotion.

**Monotone-safe staleness** [D]: a stale bundle is bounded below by the floor at any age, with no refinement premise.
The lease argument has the same shape.

**Bundle revision binding** [A·CR]: a bundle decision counts only from the revision the lease names. A local
fallback engine decides only when it holds that revision. Otherwise the bundle is unreachable and refuses. **Bundle
fail-closed protects narrowings, not the floor.**

**Deny reason** [A·CR]: a floor deny names the forbids that fired, or ***no permit matched***.

**Verified evaluator** [A·CR]: the floor tier's obligation is a mechanized semantics, an implementation checked
against it, and a decidable comparison of two policy sets. Cedar meets it and Rego does not. The floor is **linked
into the mechanism as a library**, with no process, socket or fetch.

**Schema S** [A·CR / P]: the typed lift's type, enforced on every request. The analyses quantify over it. The
genesis `genesis.cedarschema` is DRAFT.

**Nothing translates** [A·CR]: there is no Rego → Cedar transpiler, in either direction, in the archetype.

**The gates** [A·CR]: **totality** (never-errors), **non-vacuity** (not always-allows), **discrimination** (not
always-denies), per action over S. The genesis floor also runs **every-entry-matters** and **routing**. A failing
gate returns a counterexample request. The gates are decidable checks on the floor (ADR-0030 §5).

**Floor fitness** [O, 2]: the missing gate (NIST MEASURE 2.13). The gates show that a floor is well formed and not
vacuous. They do not show that it is *right*. It is unowned.

**Genesis floor** [P, 25]: `floor/genesis-floor.cedar`, 14 Cedar policies, gated 2026.09.24. It is **DRAFT and not
ratified**: ADR-0030 ratified the language and machinery, not a floor.

**Forbid B7** [P]: the recusal forbid in the genesis floor. Recusal is floor text, so **relaxing it is a policy-floor
relaxation** (ADR-0022 A1).

**Floor-change routing** [A·CR]: the classification is **computed, not asserted**. The analyzer decides `F′ ⇒ F`
and `F ⇒ F′`:

| Change | Authority |
|---|---|
| Tighten the policy floor | An ordinary promotion |
| Relax it, or add an exception | Anchor issuance **and** promotion |
| **Incomparable** revision | Routed as a relaxation |
| Any rules-floor change, either direction | Anchor issuance **and** promotion |

**Resident floor** [A]: the default-deny floor is pre-blessed, staged and instantiated rather than fetched, so fail-closed
works at cold start (ADR-0012).

**Vacuous floor** [D]: a floor that admits everything and discharges every property over nothing, invisibly. This
is why the gates run on the floor.

**Rules floor** [A]: the verified bound on the trust anchor (ADR-0026). The mechanism rejects any issuance that
violates it.

| Entry | Bound | State |
|---|---|---|
| R1 | `quorum = "all"` over counted grant seats | In force |
| R2 | `minGrant ≥ 2` | In force |
| R3 | Recusal | **Withdrawn**: enforced by the `Vote` envelope, so there is no issued value to bound |
| R4 | A timeout never grants | **Withdrawn**: now a mechanism constant |
| R5 | No key both in the anchor key set and on the promotion roster | In force |
| R6 | Exception-count bound, currently two | In force from 09.23 |
| R7 | No break-glass grant may authorize `Issue`, `Vote` or promotion | In force |
| R8 | Break-glass grant TTL | **Drafted**: ADR-0026 A1, pending, with four conditions unmet |
| R9 | `quorum = "all"` or `quorum ≥ 2` | In force. A **conditional entry** that binds only once R1 is relaxed |

**Parametricity** [A]: a floor entry bounds a value only if the mechanism reads it from issued rules. **Converse:**
a value fixed as a constant cannot be bounded by an entry. Checked by `RulesFloorNV` and `RulesFloorNV_rev5`.

**Empty-roster promotion** [A]: without R2, a havoc issuance sets an empty roster, unanimity over the empty set is
vacuously true, and an artifact promotes with **zero votes**.

**Floor exception** [A·CR]: a carve-out for a path that cannot be written as a subtraction. There are two:
**erasure** and **break-glass** (ADR-0013). Since ADR-0030 they are Cedar policies inside the floor, so **a bundle
can narrow break-glass**, and nothing can widen it.

**Non-composition** [A·CR]: **NC-1**: break-glass chained with erasure never yields an effect that is authorized,
erased and unattributable. **NC-2**: erasure never removes a forensic-floor record. Both were checked on
2026.09.23, with a witness that the composition is reachable.

**Per-class floors** [O, 9]: whether Build and Run share one floor or each have one over a shared core. Cedar can
state either answer, and ADR-0030 does not choose. ADR-0014 is reserved for it.

---

## 5. Authority

**Promotion** [A]: the crossing from Build to Run, for bundles, mechanism releases (floor changes included) and
Personas. **Promotion is a quorum grant** read from issued rules (ADR-0024). **A promotion is a round**, keyed by
artifact digest.

**`quorum`** [A]: either `"all"` or a grant-vote threshold *k*. The archetype value is `"all"`. The value `"any"` is
**withdrawn**: it is *k* = 1.

**Grant seat** / **veto seat** [A]: a grant seat is held by a human `Mediated` principal with a named role. A veto
seat's alphabet lacks `grant`. **Veto-seat silence is not a veto.**

**A timeout is never a grant** [A]: a mechanism constant.

**Vote binding** [A]: a vote binds to (artifact digest, gate-evidence digest, rules epoch). A change of rules epoch
voids in-flight votes.

**Gates enable voting; they do not vote** [A].

**Recusal** [A]: a **mechanism constant**. The author is removed from the counted seats, and the `Vote` envelope
refuses the author's vote. If too few seats remain, promotion is denied.

**Runtime subtraction is not promotion** [A]: e-stop, expiry, revocation and `deny=all` need no quorum. They are still
**ordered** wherever they change replicated state.

**Trust anchor** [A]: the authority that defines who votes. It is modeled as a **havoc issuer**: safety holds for
every issuance it could make (ADR-0025).

**Issuance** / **`Issue`** / **`Resign`** [A]: the anchor's actions. They are environment events that no Build
principal can express. `Resign` is defined per custody rung in the ADR-0025 annex. At archetype custody it freezes
the rules. On a threshold rung the recovery rule rotates the key. Under n−1 eviction it consumes that epoch's single
eviction.

**The intent axiom** [A]: the sole axiom. *An authentic issuance at the current anchor epoch is what the anchor
intended.*

**Infallible, split three ways** [A]: **intent** is assumed, **integrity** is modeled, **custody** is declared.

**Rules** [A]: the promotion roster and its parameters, the break-glass and erasure rosters, the anchor key set, any
relaxation of the policy floor or new exception, and **any change to the rules floor in either direction**.

**Custody** [A]: the declared pair (capture threshold, loss tolerance).

| Record | Model | (capture, loss) |
|---|---|---|
| A-0025 | Strict unanimity, n ≥ 3 (the archetype) | (n, 0) |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) |
| D-0025-1 | Threshold with recovery, in the shape of the TUF root role | (k, n−k) |
| — | Single custodian: the corpus today | (1, 0) |

**Loss freezes the rules** [A]: at archetype custody the system runs and subtracts but cannot change. The only exit
is **re-genesis**.

**Anchor capture** [A]: the headline residual. A coalition at the capture threshold can issue any
rules-floor-conformant roster. **No safety theorem covers anchor intent.**

**Two keys, both directions** [A]: a rules-floor change needs an issuance and a promotion, even to tighten.

**Genesis rules** [A]: they ship with the mechanism release and are fetched from nowhere (ADR-0027). Epoch 0 is the
root of the rules-epoch chain. The epoch-0 floor check is the `GenesisSatisfiesFloor` invariant, not a promotion.

**Privileged grant** [A]: a quorum on an anchor-issued roster, bounded by the rules floor. Ordinary Run admits are
grants too, but they are decided against a bundle, not a roster.

**Consensus for grants, local for denials** [D]: the organizing rule.

**Monotonicity, layer by layer** [D]: now eight layers (ToO §7.8):

| Layer | Statement |
|---|---|
| Decision | Consensus for grants, local for denials |
| Policy | Bundles only subtract, by composition |
| Change | Increases need consensus. Decreases need no quorum, but are ordered when they change state |
| Deployment | Degenerate forms lose theorems, never gain capability |
| Authority | Relaxing the rules needs the anchor |
| Evidence | Authority facts survive erasure and break-glass |
| Credential | Renewal only narrows |
| Time | Intervals that subtract may use a local clock. Intervals that preserve authority need trusted time |

At the pattern level it **inverts**: tightening the archetype puts every deployment into declaration debt, and
relaxing it voids published theorems.

---

## 6. The record

**Effects** [A·CR]: exactly {tool invocation, principal emission}. **Authority changes**: exactly {promotion,
anchor issuance} (ADR-0015). The qualifier that keeps the second set at two is ***change to the rules in force***.
Break-glass and erasure are admit decisions against their exception entries, so both are effects.

**The admit decision is the orderable event** [A·CR]: not the emission.

**Audit chain** [A·CR]: effect → admit → floor ∧ bundle at the lease's revision → rules epoch → issuance → intent
axiom. No link is assumed except the last.

**Decide, order, re-check** [A]: deciding and ordering are separated in time (ADR-0033 §4). The mechanism checks run
before the floor and again at apply time. An admit that fails the second run is **void**: ordered, recorded and
without effect. The floor and bundle are not re-run. The effect runs only after commit.

**Ordering is not authorization** [A]: subtractions need no quorum, but they must be ordered if they change
replicated state.

**Denials are recorded, not ordered** [A]: a denial is written unordered to the principal's round topic, as digests,
by the replica that decided it (ADR-0020). Without denials, the trail cannot tell *behaved* from *was prevented*.

**Effect exclusivity** [A·CR]: the principal reaches the world only through the alphabet. ADR-0015 makes it a
mechanism claim, which is **identical in strength to Moon & Varshney's assumed version until ADR-0022 §6 is
discharged** (ADR-0015 E2).

**Kafka's role** [P]: neither the ordering authority nor the system of record. It is a transport with a durability
window (ADR-0005, Proposed). An emission is written after commit and carries the admit's log index, the fence and a
per-lease sequence number. The reference's use of Kafka is a debt against ADR-0005 (open item 5).

**Round** [A in Run · P in Build]: in Run, a cycle of principal activity (ADR-0003). In Build, one pipeline
invocation (ADR-0021, Proposed).

**Topic per principal per round** [A]: sealed on emit completion, with per-topic ACLs, per-use-case retention,
explicit replay authorization, write-time masking and no tiered storage. **The topic is the unit of erasure.**

**Topic identity includes the rules-epoch chain** [A]: so a successor system never writes to a predecessor's sealed
topic (ADR-0003 A1).

**`after` companion topic** [A·CR]: one per round. It holds denials only, for attempts made under the round's lease
after its topic is sealed. It is bounded by a limit marker and erased with the round (ADR-0003 A2, the only
confirmation marker scoped to one amendment).

**Control-plane facts vs cognitive payloads** [A]: the archive keeps a hash and a pointer. Plaintext lives in a
separately governed store built for deletion (ADR-0004).

**Erasure** [A·CR]: a modeled event that is consensus-ordered and recorded in the log it modifies. Its authorization
lives in the verified object. **Genesis rules issue no erasure roster**, so erasure is disabled from epoch 0.

**Crypto-shredding** [A, rejected]: it leaves a verifying envelope over unreadable ciphertext, which no auditor can
tell from suppression.

**Replay** [A]: reconstructs what crossed the membrane, including refused attempts (ADR-0020). The Observer and
replay read the same stream.

**Legibility** [A·CR]: replaces "immutable". *Every admitted boundary event remains readable by the declared audit
authority for the declared horizon.* Compartmentation subtracts the reader set, and it is not erasure.

**Forensic floor** [A·CR]: six classes that cannot be erased for the horizon: **F1** admit decisions · **F2** stop
attribution · **F3** promotion votes · **F4** anchor issuances · **F5** break-glass invocations · **F6** erasure
events (ADR-0028). Each class is a floor denial on the erasure envelope. No cognitive payload is in the floor.

**Where a vote lives** [A]: the authoritative vote is the admit decision in the consensus log, which F3 retains. The
round-topic emission carries a pointer to its commentary, and erasure removes only the commentary.

**Demand type 5** [A·CR]: "hide that a record existed". It is **declined**, because it conflicts with NC-2 and F6.

**Forensic horizon seam** [O, 10]: the horizon is the rules-epoch chain, and re-genesis starts a new chain. The
successor's read access is carried as a re-genesis migration obligation.

---

## 7. Detection and the model

**Observer** [A]: the detection layer. Every finding is **deny-only**.

**Placement** [A]: Observer replicas never share a device with the Thinker they watch, or with each other (ADR-0008).
**A Byzantine quorum of co-resident replicas is arithmetic fiction.**

**Scoping, reversed in effect** [A → O, 6]: ADR-0008's shared Observer group stands in text. ADR-0023 makes the
archetype **per-principal Observers plus a cross-principal correlator**. The superseding record is unwritten, and it
must also re-home ADR-0024's veto seats.

**Cross-principal correlator** [O]: a noun, with no record, alphabet or placement.

**Monoculture** [D]: an Observer should come from a different model family than the agents it watches.

**Build has an Observer** [P]: ADR-0021, Proposed. It is blocked on ADR-0003's no-tiered-storage clause (open item 4).

**LTRO** [D]: Listener / Thinker / Reader / Observer, the internal decomposition of an agent principal. The
**Reader** reads logits and may colocate with the Thinker.

**Seat** [A]: the binding point for a Persona, and the unit of attestation and attribution. A principal is the unit
of authority and eviction.

**Persona** [A]: a signed, versioned Build artifact that binds a model to its complete runtime configuration
(ADR-0016). **TOPAK verifies Personas; it does not verify models.** The Persona is a lease field, so revoking a
Persona is a targeted revocation.

**Verification vs suitability** [A]: signature, hash and provenance integrity are preconditions. Evaluations are
evidence. **Evaluation is deny-only.**

**Provenance degradation** [A]: **verified** → **attested** → **asserted**.

**Lineage** [A]: the archetype admits only **in-house pre-trained Personas from two independent lineages** (ADR-0017).
The admission clause stands, but its ordering-primacy clause is reversed in effect by ADR-0023.

**Seat distinctness** [A]: the Observer's Persona differs from the Thinker's **by lineage**.

**Independence criterion** [O, 20]: owed by ADR-0017. Until it exists, `Contained` is unreachable at any rung. ADR-0035
proposes one (§10).

**Typed lift split** [A]: the decoder ships in the Persona, and the validator lives in the mechanism (ADR-0018).
**Decoder–alphabet compatibility** under a change to S is open (item 17).

**Decode observability** [A]: `none` is the only unconditional value. `topk_logprobs` is admissible for conformance
and substitution detection, never for claims about `L` (ADR-0019).

**Silent substitution** [D]: a provider changes weights with no event anywhere. Pinning makes it a detectable
identity mismatch. **No staleness argument covers Personas.**

---

## 8. Time, variation, boundaries

**Clock model** [A]: stated in ADR-0032. **Clocks buy liveness, never safety.** Epoch fencing carries safety.

**Trusted by failure direction** [A]: an interval whose failure **subtracts** (lease expiry, passive e-stop, vote
timeout) may use a local monotonic clock with an asymmetric margin that errs early. An interval whose failure
**adds or preserves** authority (break-glass TTL, Persona expiry, re-attestation) needs trusted time.

**No safety decision reads a principal-supplied clock** [A]: a timestamp in a payload is content, not a fact.

**`W + L + D < T_irrev`** [A]: the timing property, declared per effect class. **`W`** is the propagation window,
about a second, guaranteed by the mechanism. **`L`** is Observer detection latency, an emergent property, and
**unmeasured**. **`D`** is the human response budget, an organizational commitment. **`T_irrev`** is the time until an
effect becomes irreversible. Where no budget fits, **the effect must not be in the alphabet.**

**E-stop** [D]: **passive** (lease non-refresh, subtracts) · **active** (unilateral human stop, subtracts) ·
**break-glass** (quorum, **adds**).

**HITL / HOTL / HOOTL** [D]: defined by enabling condition. Build affords HITL. Run's roughly one-second window leaves
HOTL.

**Boundary register** [D]: fourteen boundaries, each with a cadence, an instant, an interval of untruth and behavior
when unavailable. **B8** (Persona evolution) is the most critical. The **instants** are promotion, seal, fence and
revoke.

**Archetype** [A·CR]: the unique maximum of the parameter lattice. It is a reference point. **Nobody ships the
archetype** (ISO 26262 SEooC precedent).

**Degeneracy** [A·CR]: a form reached by driving named parameters to limiting values. Its **effect is premise loss,
not weakening** (ADR-0023). *Reduced* is the operational register.

**Admission test** [A·CR]: a variation is a rung only if it is reachable by parameter limit, and it must also be
checked for **type changes**. A capability the archetype lacks is a finding about the archetype.

**Rung** (degeneracy) [A·CR]: a position on one axis. A deployment is a tuple.

**Declaration record** [A·CR]: kind · parameter · archetype value · deployed value · premises falsified · theorems
voided · type changes · optional mitigation · composition note.

**Kind** [A·CR]: a **mechanism degeneracy** changes a value inside the verified object and ships as a release. A
**declaration degeneracy** changes something outside it and reopens nothing.

**Composition note** [A·CR]: required above one parameter. It names the **delta**: theorems voided jointly but not
individually. **A missing note is not an empty delta.**

**Type change** [A·CR]: a participant moving between the gate and principal. It moves the TCB.

**Declared records** [A]: D-0024-1 (k-of-n) and D-0024-2 (single signer), on approver fault tolerance. A-0025,
D-0025-1 and D-0025-2, on anchor recoverability. **A-0030** and **D-0030-1** (a Rego floor, *measured* rather than
*proven*), on floor verification.

**Axes named so far** [D]: Persona provenance, event-log legibility, Observer scoping, effect-stream role, arguably
HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability and floor verification. The set is not
enumerated.

**Archetype-evolution record** [O, 7]: holds archetype versioning, the dominance rule and non-increasing TCB. Until it
exists, **nothing bounds how the archetype grows.**

**Assumptions of use** [D]: ToO §13, framed as a SEooC. **A deployment that fails them does not inherit the
theorems.**

| # | Assumption |
|---|---|
| A1 | Effect exclusivity is enforced by a mechanism |
| A2 | Every allowlisted tool is hermetic |
| A3 | Anchor key-holders are honest at the declared capture threshold |
| A4 | Grant seats review independently |
| A5 | A trained, authorized human is present for break-glass, quarantine release and `D` |
| A6 | Trusted time exists for intervals that preserve authority |
| A7 | The deployment declares its degeneracies |
| A8 | Confirmation-required records are cited as author-ratified |
| A9 | The mechanism's replicas are not compromised |
| A10 | Each effect class declares `T_irrev`, and the budget holds |

---

## 9. Genesis, process, and the corpus

**Genesis** [A]: the current process, **not a degeneracy**. Custody is declared as Scott, sole custodian, (1, 0).

**Unilateral ratification** [A]: the custodian may ratify any record that has decision text.

**Confirmation-required** [A]: a ratified record carrying a proof obligation over privileged paths (**C1**), an
exhaustiveness or confinement claim (**C2**), a reversal in effect (**C3**), or the resolution of such a debt
(**C4**). The count at G3 is **nine**. **A marking may be scoped to an amendment** (ADR-0003 A2).

**Bootstrap set** [A]: ADR-0024 to ADR-0027. It **cannot carry the marker**, because confirming it under itself
would be circular. **Since ADR-0029 A2 it is reviewed at the bootstrap gate** with the rest of the corpus.

**Bootstrap trigger** [A]: (a) a drafted TLA+ bootstrap specification of five modules (`Genesis`, `Anchor`,
`RulesFloor`, `Promotion`, `BreakGlass`), of which two exist, **and** (b) an **independent review of the entire
corpus** at one manifest digest (ADR-0029 A2). **The trigger is permission, not obligation.**

**Genesis bundle** [A]: the corpus manifest, the specification digest (checked or drafted-only), the review
attestation and the genesis rules. Every key-holder signs it, and that is issuance epoch 0. **It is the only artifact
never promoted.**

**Headcount** [A]: an archetype bootstrap needs **five** humans: three key-holders, two grant seats, and R5
disjointness. It needs six if the author holds a seat. **A solo bootstrap is not a bootstrap.**

**Re-genesis** [A]: the exit from frozen rules. It creates a **successor system**. **Migration** is open (item 10).

**Genesis debt ledger** [A]: the per-checkpoint tally of the confirmation set. There is no forcing function: the debt
is visible, not bounded.

**Debts on the face** [A]: obligations an accepted record carries openly in its status note. Examples are ADR-0030's
six, ADR-0031's five, and ADR-0033's Kafka row.

**G checkpoint** [C]: the state of record. G3 (2026.09.25) is current. A cut is immutable, and corrections go to the
next one.

**Theory of Operation** [C]: the narrative. **It is not the state of record.** Rev 7 is current.

**Batch** [C]: a ratification group. Batches 5–9 were ratified on 09.25, and the records tag them ⟨B5⟩ … ⟨B9⟩.

**Conventions** [C]: G-C1 (files are cited by digest) · **a tree is cited by manifest** plus commit · **drift pins**
(`mechanism/corpus-pins.sha256`) · **pointer errata** (a promised pointer, no decision text) · **dependent entries**
(a ratification row with no text change) · **one results file per run**, never overwritten.

**Havoc semantics** [A]: modeling an agent as capable of anything its alphabet allows.

**Mutation** / **witness** [A/D]: every TLA+ property ships with a mutation that must fail and reachability witnesses
that must be violated. **The floor has a decidable non-vacuity gate. TLA+ still does not**; for TLA+ it is a
convention.

**Too-coarse model** [D]: a model can be too small to see a finding. `Lease.tla`'s single global epoch hid finding 5.
Four humans made R1's mutation hold vacuously. **A threshold needs at least three counted seats** before any
threshold property means anything.

**Checked, not proved** [C]: TLC at small constants is a discrimination test. **No theorem is proved** (G3 §8).

**Refinement** [D]: two senses. By composition (policy), which the corpus has. Specification-to-implementation
(formal methods), which it **does not have**.

**Reference implementation** [R]: `mechanism/`, the admit path end to end. It is **evidence, not the verified
object** (ADR-0033 §1). It is cited by manifest and commit, it has never been promoted, and nothing in it is in any
TCB. It issues only rung-0 leases, so it fails A1. **Twenty-two assumptions and seventeen gaps** are tagged in the
code (`GAPS-AND-ASSUMPTIONS.md`).

**Reference findings 1–11** [R]: routed to records in ToO §15. Three needed running code to find (1, 4 and 9). Only
finding 9, proposer retry in the drafted `Paxos` module, is still open (item 24).

**Crash-recovery replicas** [A]: the consensus replicas are not Byzantine (ADR-0033 §3). **Replica authentication and
Byzantine replicas** are open (item 23). This is assumption A9.

**TCB declaration record** [O, 16]: it is unwritten. It is owed the engine-divergence and Byzantine-replica residuals.

---

## 10. After G3: Proposed records

Both records were written on 2026.09.25, after the G3 cut. **Neither is Accepted**, and neither is in G3's manifest.

**Attestation rung** [P]: ADR-0034 proposes the ordering: **0** none · **1** asserted by the launcher · **2**
measured boot · **3** confidential VM with an independent verifier. **The archetype is rung 3.** Rungs 0–2 are
declared degeneracies. Attestation happens **at lease grant** and lands in the lease's `confinement` field. It would
close ADR-0022 §6 for Build and G3 item 19.

***Contested*** [P]: Sokolov's verdict: the signature is valid but the measurements diverge. Under ADR-0034 the
response is refusal plus a **targeted revocation of the principal**. **Rung 1 cannot produce *Contested*.**

**Lineage projection** [P]: ADR-0035 proposes that a Persona's lineage record is **projected from the Build log**,
not taken from the trainer's manifest. A lineage that can only be declared is **D-0035-1**.

**Exclusion rules E1–E5** [P]: two lineages are independent unless one of these fires: **E1** shared weights ·
**E2** shared generators · **E3** corpus overlap above θ · **E4** same architecture family and tokenizer · **E5**
shared curators. Plus the **distillation rule**. The rehearsal is in `slm/`, and the θ values there are
placeholders.

---

## 11. Outstanding

These terms name a hole. Each one points to the G3 §7 open list.

| Term | Item |
|---|---|
| **Sandbox gap** | 1 |
| **Floor fitness** | 2 |
| ADR-0021 (Build Observer) · ADR-0005 (Kafka) | 4 · 5 |
| ADR-0008 and ADR-0017 supersessions | 6 |
| Archetype-evolution record | 7 |
| R8, break-glass TTL | 8 |
| Per-class floors (ADR-0014) | 9 |
| Re-genesis migration | 10 |
| Custody beyond (1, 0) | 11 |
| Derived documents not regenerated | 12 |
| Run's alphabet | 13 |
| Solver trust for routing's "implies" results | 15 |
| TCB declaration record | 16 |
| Decoder–alphabet compatibility | 17 |
| **Bundle signing** (bundle identity is a content revision until it exists) | 18 |
| Attestation rungs · independence criterion · Persona expiry and lineage | 19 · 20 · 21 |
| Lifting a revocation | 22 |
| Replica authentication | 23 |
| Finding 9 | 24 |
| Genesis floor and S, DRAFT | 25 |

These are also unowned and not numbered: **`Invoke` hermeticity** · the **cross-principal correlator** · the
**Observer quarantine gate** · **delegation / on-behalf-of** · **flow** (CR-6) · the **residual-risk statement**,
headed by anchor capture.

---

## 12. Adjacent vocabulary

These are carried from the 09.17 glossary §12 unchanged, with three additions: **Cedar** and its Lean-verified
semantics and **SymCC** analyses (now the floor instrument) · **MCP** (the reference's agent interface) ·
**confidential VM** and **RATS verdicts** (ADR-0034).

---

## 13. Terminology hazards

These collisions are live. Several are new since 09.17.

1. **"A1", "A2" and so on: four alphabets.** Amendments (ADR-0003 A1), assumptions of use (A1–A10), archetype
   declarations (A-0025, A-0030), and the readiness key. *"ADR-0003 A2"* and *"assumption A2"* are unrelated.
2. **"B" and a number: four referents.** Boundaries (B8, B12, B14), floor policy IDs (forbid **B7**), ratification
   batches (⟨B5⟩–⟨B9⟩), and ADR ratification-table rows (ADR-0026 B4, ADR-0033 B8). *"B7"* and *"B8"* each have more
   than one live meaning.
3. **"E" and a number: errata and exclusions.** ADR-0031 E1 and ADR-0015 E2 are errata. ADR-0035's E1–E5 are
   independence exclusions.
4. **"R" and a number: rules-floor entries and record revisions.** "0031 at R3" is a record revision. "R3" alone is a
   withdrawn rules entry. The readiness key's **R** is a third use.
5. **"G" and a number: checkpoints, conventions and gaps.** G1–G3 are checkpoints, **G-C1** is a convention, and
   **G5** in `mechanism/` is a code gap. Name the three floor gates; don't letter them.
6. **"Rung": now three orderings.** ADR-0023 degeneracy rungs (per axis), confinement attestation rungs 0–3
   (ADR-0031 field, ADR-0034 Proposed), and provenance rungs on ADR-0017's axis. `slm/` says "every round runs at
   rung 0", meaning **attestation** rung. Always qualify.
7. **"Floor": now five things.** The policy floor, the rules floor, the forensic floor, floor fitness, and **the
   genesis floor** (a DRAFT text, as distinct from the machinery that checks one). There is also "floor minimum", a
   seat count.
8. **"Declared": two opposed senses.** A **declaration** degeneracy reopens nothing (ADR-0023). A **declared**
   lineage record is the *weakest* strength (ADR-0035 D-0035-1). Declared custody is a third use.
9. **"Revocation" vs "fence".** A targeted revocation ends matching leases. An epoch fence ends every round. Earlier
   text used "fence" for both.
10. **"Agent": three referents.** The A in TOPAK, the LLM inside a seat, and OPA (Open Policy *Agent*).
11. **"Epoch": four counters.** Rules epoch, anchor epoch, lease epoch, and deployment epoch. The fence is a log
    index, not an epoch.
12. **"Round": Build and Run differ.** A promotion is also a round. Always qualify.
13. **"Byzantine": agents, not replicas.** Agents are Byzantine. The control-plane replicas are crash-recovery
    (ADR-0033 §3), which is now declared.
14. **"Proved": retired** (CR-25, rev 7 erratum). Say *checked* or *must hold*.
15. **"Degenerate"** collides with TLA+'s "degenerate behavior" (the ADR-0023 obligation) and reads as pejorative.
    Use *reduced* in operational prose.
16. **"Confirmation-required" count drift.** G3 and rev 7 say **nine**. ADR-0029's status note, after A2 was
    ratified on 09.25 following the G3 cut, adds a **C3 marker for A2 only**, which would make ten. G4 has to say
    which.

---

## 14. Retired wording

Rows added since 09.17 come first. The 09.17 table (CI/Orch, "semantic containment", the ladder, "immutable",
crypto-shredding as mechanism, Kafka as system of record, "strictly stronger than Moon & Varshney", the `L`/`D` swap,
§4.2 → §4.6, "Varshnay") still stands.

| Retired | Replacement | Authority |
|---|---|---|
| `bundle ⊑ floor` decided at promotion, by SMT over Rego | A property of composition, for every bundle | ADR-0030 §1 |
| O = OPA and Rego | O = a verified floor evaluator plus a bundle engine | ADR-0030 §2 |
| `quorum = "any"` | A threshold *k*, with R9 keeping *k* ≥ 2 | ADR-0024, ADR-0026 |
| Recusal as an issued value; R3 | A mechanism constant in the `Vote` envelope; R3 withdrawn | ADR-0024, ADR-0026 |
| Relaxing recusal is a mechanism release | A policy-floor relaxation: issuance and promotion | ADR-0022 A1 |
| `W < L < D` as the safety property | `W + L + D < T_irrev` per effect class; the ordering is a magnitude description | ADR-0032 §4 |
| "Proved", "proven" | "Checked", "must hold" | G3 §8; CR-25 |
| "The bootstrap set gets no independent review, ever" | Reviewed at the bootstrap gate with the whole corpus | ADR-0029 A2 |
| `Resign` "defined nowhere" | Defined per custody rung | ADR-0025 annex |
| Lease attenuation, lease rank, fence token **[S]** | Renewal only narrows; fence = Paxos log index at grant | ADR-0031 |
| Asymmetric margin **[S]** | A local monotonic clock with a margin that errs early | ADR-0032 |
| Confinement rungs, *Contested* **[S]** | Attestation rungs 0–3, *Contested* | ADR-0031 §3; ADR-0034 (Proposed) |
| One epoch fence for every revocation | Targeted revocation plus epoch fence | ADR-0031 |
| "Clock model: unstated" | Stated | ADR-0032 |
| Denials not recorded | Recorded, unordered, as digests | ADR-0020; reference finding 11 |
| Monotonicity "at five layers" | Eight layers | ToO rev 7 §7.8 |

---

## Sources

**Basis.** `checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md` · `checkpoints/topak-theory-of-operation-2026.09.25-rev7.md`
· the records they cite, at their G3 digests.

**After G3, marked where used.** ADR-0029 A2 (ratified 09.25, after the cut) · ADR-0034 and ADR-0035 (Proposed) ·
`derived/topak-critical-review-2026.09.25.md` (CR-21 to CR-26).

**Superseded.** `derived/topak-glossary-2026.09.17.md`, whose §12 is carried by reference.
