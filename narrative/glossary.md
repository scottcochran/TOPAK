# TOPAK — Glossary

**2026.09.29** · derived · regenerated · DRAFT

**Basis.** Genesis Checkpoint G5 (2026.09.29) and Theory of Operation revision 9 (2026.09.29), with the record files
they cite. Where the two disagree, G5 wins. The four Proposed records (ADR-0005, ADR-0021, ADR-0035, ADR-0036) appear
under their subjects, tagged **[P]**, and are collected in §10.

**What this supersedes.** The 2026.09.26 glossary, cut against G3 and rev 7, which predated G4 and G5 (G5 open item
12). Every entry was re-read against G5; the ones G4 and G5 changed are rewritten, and §14 lists the wording that
retired. The 09.17 session vocabulary stays dropped or placed as the 09.26 glossary placed it.

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
| **[C]** | Checkpoint convention, fixed by G1–G5 |
| **[R]** | The reference implementation (ADR-0033). It is evidence, not the verified object |
| **[O]** | Outstanding: the term names a hole rather than a mechanism. Numbers refer to the G5 §7 open list |
| **[X]** | Superseded: the term's record is superseded and its text is no longer in force |

Record status is G5 §1 and is not restated here except where the status changes what a term means.

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

**Principal** [A]: *anything evictable by an authority other than itself.* Principals are inside the proofs. **A
principal holds exactly one seat** (ADR-0037 §1), so the lease's `principal` and `seat` determine each other.

**At the gate** [A]: whatever is not evictable. It sits outside the proofs and is carried as an assumption or a
declaration. **Resignation is not eviction** (ADR-0002 A2). At archetype custody the anchor key-holders are at the
gate. At degenerate custody they become principals, which is a type change (§8).

**`Contained(p)`** / **`Mediated(p)`** [A·CR]: a principal that reaches the world only through its alphabet, and one
with some effect path that no action names (a shell, egress, a git remote). Safety theorems quantify over `Contained`
principals. `Mediated` principals get attribution and authorization, not containment. **Rung 0 is `Mediated`,
always.** `Contained(p)` has **four conjuncts** (ADR-0034 §4): a live lease at rung ≥ 1 on an *Attested* verdict at
the declared rung; a profile meeting P3–P5; an in-house Persona; and the lineage-independence criterion in force.
The fourth is ADR-0035, Proposed, so **`Contained` is unreachable at every rung today.** ADR-0037, ADR-0038 and
ADR-0039 add and remove no conjunct.

**Cell** [A·CR]: the principals seated around one Thinker for a round (ADR-0037 §1). A cell holds no lease, speaks no
alphabet and cannot be evicted as a unit; it names a binding, as a round does. **An LTRO is a cell, not a
principal.**

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

**Alphabets bounded by seat kind** [A·CR]: only a `thinker` seat is ever issued `Draft`, `Invoke`, `Submit` or
`RunInvoke`; an `observer` seat reads, emits and, on the veto roster, denies; a `grant` seat reads, emits and votes
(ADR-0037 §4). Stated in the floor as **forbid B10** and a tightened **B6**, and checked by the grant path first.

**Confinement obligation** [O, 1]: ADR-0022 §6. No shell, no egress, no filesystem outside the workspace and corpus,
and no path to the artifactory except `Submit`. §6 is the one section of ADR-0022 that is **not ratified**. The gap
it leaves is the **sandbox gap**, now in two halves: the design half is closed by ADR-0034, the mechanism half is
open, and every reference lease is rung 0.

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

**Renewal only narrows** [A·CR]: a renewal may narrow the alphabet or shorten the TTL. It keeps the bundle, the
round, the role and, since ADR-0031 A1, **the confinement digest and rung**; changing any of them needs a grant. A
renewal that lowered the rung was a silent downgrade reachable through the renewal path, and the records never met
in a check until `Confinement.tla` modeled renewal. So **tightening a live round ends it.**

**Cross-round coverage** [A·CR]: in Run, a Thinker's lease for round *r+1* is granted only once a cell Observer has
read round *r* to its seal (ADR-0039 §2). Build needs no cross-round rule, because its only egress is promotion.

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

**Genesis floor** [P, 25]: `floor/genesis-floor.cedar`, 16 Cedar policies, schema S and the values file, gated
three times, last on 2026.09.29. It is **DRAFT and not ratified**: ADR-0030 ratified the language and machinery,
not a floor. The mechanism compiles all three in and refuses any other bytes.

**Values file** [P]: `floor/genesis-values.json`, the third file of the floor bundle: the numbers the typed lift
reads that Cedar text cannot hold, `K`, `T_obs` and ADR-0035's unset θ (ADR-0039 §1). Relaxing a value is an
issuance and a promotion. **Every number in it is a placeholder**, a deployment or rung choice, and the file says so.

**Forbid B7** [P]: the recusal forbid in the genesis floor. Recusal is floor text, so **relaxing it is a policy-floor
relaxation** (ADR-0022 A1).

**Forbid B10** · **B6** [P]: only a `thinker` seat authors, in either domain; a vote is permitted from the grant
roster only for a `grant` seat and from the veto roster only for an `observer` seat (ADR-0037 §4).

**Forbid R3** [P]: `R3-observer-live`. A `RunInvoke` or `RunEmit` under a `thinker` seat is refused when no cell
Observer is live (ADR-0039 §2). It applies to break-glass too. An observer seat's own emissions, its heartbeats
among them, are not coupled.

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
seat is held by **every cell Observer and every correlator in Build** (ADR-0024 A2.1, from ADR-0038 §6) and its
alphabet lacks `grant`. **Veto-seat silence is not a veto**, but **an absent Observer stalls**: a promotion completes
only if a veto seat independent of the author was leased for the round (A2.2) and the author's cell Observer reported
coverage to the seal (A2.3). Both are mechanism constants in the tally, as recusal is. A2.2 is unbuilt in the
reference (`mechanism/` G18).

**Coverage** [A·CR]: a cell Observer's watermark at or beyond the seal of the watched round (ADR-0039 §3). A fact, not
a "no finding" attestation.

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

**Monotonicity, layer by layer** [D]: now twelve layers (ToO §7.8):

| Layer | Statement |
|---|---|
| Decision | Consensus for grants, local for denials |
| Policy | Bundles only subtract, by composition |
| Change | Increases need consensus. Decreases need no quorum, but are ordered when they change state |
| Deployment | Degenerate forms lose theorems, never gain capability |
| Authority | Relaxing the rules needs the anchor |
| Evidence | Authority facts survive erasure and break-glass |
| Credential | Renewal only narrows, and keeps the rung |
| Confinement | A principal below the declared rung is refused, never granted lower |
| Lineage | The projection over-approximates, and adding to it can only fail a pair |
| Time | Intervals that subtract may use a local clock. Intervals that preserve authority need trusted time |
| Seat | Only a thinker seat is issued a variant that writes, runs or offers |
| Detection | Observers combine by any-of, and coupling only refuses: more Observers never lower safety |

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
separately governed store built for deletion (ADR-0004). A **heartbeat** is a fact and enters the log verbatim; a
Thinker's **raw emission** is payload.

**Raw emission retention** [A·CR]: at the archetype, the Thinker's raw emission is written to its round topic beside
the typed action it decoded to, under the same ACL and erasure unit, for one purpose: re-run the decoder and compare
(ADR-0037 §3). It recovers **decoder faithfulness**, never intent. Optional below the archetype: **D-0037-2**.

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

**Observer** [A]: the detection layer. Every finding is **deny-only**. Since ADR-0037 an Observer is an `observer`
**seat**: a principal with its own lease, Persona and topic, evictable alone.

**LTRO** [A·CR]: Listener / Thinker / Reader / Observer. **Not a principal**: a cell of principals (§2), in which the
Thinker and the Observer are seats and the Listener and the Reader are stages (ADR-0037 §2).

**Seat** [A]: a slot declared in the issued rules, held by one principal, with a **kind**. The binding point for a
Persona and the unit of attestation and attribution. Two senses meet here: the LTRO position (ADR-0016) and the
promotion-roster slot (ADR-0024); the kind separates them.

**Seat kind** [A·CR]: `thinker`, `observer` or `grant` (ADR-0037 §2). Fixed at declaration; bounds the alphabet a
grant may issue (§2); carried into schema S.

**Stage** [A·CR]: a position in the cell that holds no Persona and no lease: the **Listener**, which delivers the task
and the admitted `Read`s and makes no choice, and the **Reader**.

**Reader** [A·CR]: a check, not a seat. Its two admissible uses (ADR-0019) produce **facts** the cell Observer
consumes: decoding conformance, which may admit only at a rung that attests inference and until then may only deny,
and substitution detection, whose threshold is the Observer's (ADR-0037 §3). The interpretation ADR-0018 gave it is
not kept. It runs beside the Thinker, inside the guest at rung ≥ 1, so everything it produces is the guest's own
report. Logprobs are monitored and not retained.

**Who forms the emission** [A·CR]: the Thinker's Persona, weights and decoder together; the mechanism's validator
admits it. The Reader was never in that chain (ADR-0037 §3, ADR-0018).

**Cell Observer** · **correlator** [A·CR]: the archetype has **one `observer` seat per cell** watching its Thinker,
plus a **correlator**, an `observer` seat with no cell that watches every cell in its domain (ADR-0038 §1). The
correlator is ADR-0008's shared group under a new name and a narrower job. A compromised cell Observer costs one
cell's detection; a compromised correlator costs cross-cell detection only.

**`W(p)`**, the watched-by relation [A·CR]: the `observer` seats holding a read authorization on `p`'s round topic,
its cell Observer and the domain's correlators (ADR-0038 §2). A fact in the mechanism's state. **Not realized as an
ACL in the reference**: cells are declared, not enforced (`mechanism/` I8).

**What the correlator reads** [A·CR]: at the archetype, every cell's admits and denials, cell Observers' findings and
the Reader's facts, the typed envelopes, and the payloads under the ACL (ADR-0038 §3). A facts-only correlator is a
permitted narrowing, declared on D-0038-2. **Its detection function is unspecified** [O, 43].

**Placement** [A·CR]: no `observer` seat shares a device with a Thinker it watches, and no two members of `W(p)` share
a device (ADR-0038 §4, carrying ADR-0008's rule forward). The reason is correlated failure and an effect path through
device memory, not quorum arithmetic. The Reader stage may colocate.

**Any-of** [A·CR]: a finding from any member of `W(p)` takes effect; **there is no Observer quorum** (ADR-0038 §5).
More Observers never lower safety and may lower availability. A quorum would let a compromised majority suppress an
honest finding (`Observers.tla` `M_QUORUM`).

**Heartbeat** · **watermark** [A·CR]: the fixed-schema fact an `observer` seat emits to report liveness: a watched
round topic and the sequence number through which it says it has read (ADR-0039 §1). Watermarks are kept per seat
and per round and only rise. A heartbeat is honest or refused: never above what exists, never falling, never from a
non-observer, never naming a round outside the observer's reach.

**`heard(o)`** · **`mark(o, r)`** [A·CR / R]: when the mechanism last admitted `o`'s heartbeat, on **this replica's**
clock, like lease expiry; and `o`'s watermark for round `r`, replicated from the log.

**`live(o)`** [A·CR]: a live lease, fewer than `T_obs` since `heard(o)` with the asymmetric margin, and
**`seq − mark < K`**, the strict form, so that after the admit being decided at most `K` are unread. The clock half is
checked at decide only; the deterministic half is re-checked at apply (ADR-0039 §1 R5).

**Coupling** [A·CR]: every Run admit under a `thinker` seat needs a live cell Observer (**R3**); a Thinker's next round
waits for coverage of its last; a Build promotion waits for coverage of the author's round; **the correlator is never
coupled** (ADR-0039 §2–§4). Coupling only refuses. A dead, partitioned or starved Observer stops its own cell and
nothing else, and the Thinker waits rather than being evicted.

**Presence is not progress** [D]: a fresh heartbeat with an unchanged watermark renews `T_obs` and nothing else; the
Thinker stays refused for its backlog. `Coupling.tla` `M_MARK` is the rule that forgets this.

**`K`** · **`T_obs`** · **`R`** [P]: the unread-emission bound and the heartbeat freshness interval, policy-floor values
in the values file; the round bound, a mechanism parameter per domain (ADR-0039 §1). `K < R` or the coupling check is
vacuous, refused at startup. **Placeholders**: `K` 8, `T_obs` 5000 ms, Run's `R` 64.

**What coupling bounds** [A·CR]: not `L`, which stays unmeasured, but the count next to it: at most `K` of a Thinker's
emissions unread by an Observer that has reported within `T_obs`, given an honest watermark.

**Collusion** [O]: the CR-2 case coupling cannot see. A colluding Observer heartbeats, reports a watermark and finds
nothing, all its own assertions. Lineage independence is the only cover, the correlated-miss test the only measure,
and **detection fails open against a colluding Observer** belongs on the residual-risk statement (ADR-0039 §5).

**Break-glass under a dead Observer** [A·CR]: R3 couples break-glass too, ratified as written; reopening it is an
amendment (G5 item 49).

**Monoculture** [A]: an Observer should come from a different model family than the agents it watches. The predicate
now has one pair per cell to cover.

**Build has an Observer** [P]: ADR-0021, Proposed. Since R3 it follows ADR-0038 placement. It is blocked on ADR-0003's
no-tiered-storage clause (open item 4).

**Quarantine gate** [O, 48]: the 09.10 design's *hold*. It is `K = 0` with a hold instead of a wait, and under the
strict form `K = 0` admits nothing, so the hold needs its own mechanism.

**Persona** [A]: a signed, versioned Build artifact that binds a model to its complete runtime configuration
(ADR-0016). **TOPAK verifies Personas; it does not verify models.** The Persona is a lease field, so revoking a
Persona is a targeted revocation. Its seat-binding field takes the values `thinker` and `observer`.

**Verification vs suitability** [A]: signature, hash and provenance integrity are preconditions. Evaluations are
evidence. **Evaluation is deny-only.**

**Provenance degradation** [A]: **verified** → **attested** → **asserted**.

**Lineage** [A]: the archetype admits only **in-house pre-trained Personas from two independent lineages** (ADR-0017).
The admission clause stands, but its ordering-primacy clause is reversed in effect by ADR-0023, and that
supersession is unwritten (item 50).

**Seat distinctness** [A]: the Observer's Persona differs from the Thinker's **by lineage**. One pair per cell,
(`thinker`, `observer`), enforced where refusal stalls (ADR-0035 §5).

**Persona granularity** [A·CR]: two `thinker` seats on one Persona are two principals in two cells, and this is
permitted (ADR-0037 §5).

**Independence criterion** [P, 20]: ADR-0035, Proposed at R3. Until it is in force, `Contained` is unreachable at any
rung (§10).

**Typed lift split** [A]: the decoder ships in the Persona, and the validator lives in the mechanism (ADR-0018). Its
Reader scope correction is reversed in effect by ADR-0037 (C3); the split stands. **Decoder–alphabet compatibility**
under a change to S is open (item 17), and is the trigger to revisit a **decoder seat**, the option ADR-0037 did not
take.

**Decode observability** [A]: `none` is the only unconditional value. `topk_logprobs` is admissible for conformance
and substitution detection, never for claims about `L` (ADR-0019). Conformance admits only where inference is
attested (B12 dependent entry).

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
*proven*), on floor verification. **D-0034-1** to **D-0034-4** (rung 2, rung 1, a native tool, rung 0), on
confinement. **D-0037-1** (no Observer in a cell), **D-0037-2** (no raw emission retained), **D-0038-1** (the shared
group only: ADR-0008 as ratified), **D-0038-2** (no correlator), **D-0039-1** (Run uncoupled). In Proposed records,
D-0035-1 and D-0036-1. None is a deployment declaration.

**Properties lost** [O, 40]: the field ADR-0023 §6's schema lacks. The five Observer and retention degeneracies void
no safety theorem and state their losses in prose: a detection claim, an audit, a bound (ADR-0037 finding 6).

**Attestation rung** [A·CR]: **0** none · **1** asserted by the launcher · **2** measured boot · **3** confidential VM
with an independent verifier (ADR-0034, Accepted at G4). **The archetype is rung 3**; rungs 1 and 2 are declared
degeneracies, rung 0 is `Mediated` always. Attestation is a condition of the grant and lands in the lease's
`confinement` field; **no silent downgrade** at grant or renewal.

**Confinement profile** [A·CR / P]: a promoted artifact fixing seven clauses **P1–P7**: one channel, a measured
read-only root, no interpreter reachable, Wasm tools only, inference inside, one principal per guest and one guest
per round, its own reference values (ADR-0034 §1). In the reference a JSON file whose digest is the lease's
confinement digest (ADR-0036 §1, Proposed), each clause `pass`, `fail` or `vacuous` with a reason.

**Declared profile** [P]: a rung-0 grant may name a profile; its verdict is then derived from the declared clauses,
*declared by the operator and verified by nobody* (ADR-0036 R1). The trusted base at rung 0 stays empty. The profile
is the constant across rungs and the rung the variable.

***Contested*** [A·CR]: signature valid, measurements diverging. Refusal plus a targeted revocation of the principal.
Rung 1 cannot produce it.

**Axes named so far** [D]: Persona provenance, event-log legibility, Observer scoping (archetype fixed: per cell plus
correlator), effect-stream role, arguably HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability,
floor verification, confinement rung, lineage strength, Observer coupling and emission retention. The set is not
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
| A11 | The lineage-independence criterion is in force before archetype provenance is declared |
| A12 | Every Run Thinker's cell Observer keeps up: heartbeats within `T_obs`, watermark within `K`, coverage to each seal |
| A13 | The cell Observer is not colluding with its Thinker |

---

## 9. Genesis, process, and the corpus

**Genesis** [A]: the current process, **not a degeneracy**. Custody is declared as Scott, sole custodian, (1, 0).

**Unilateral ratification** [A]: the custodian may ratify any record that has decision text.

**Confirmation-required** [A]: a ratified record carrying a proof obligation over privileged paths (**C1**), an
exhaustiveness or confinement claim (**C2**), a reversal in effect (**C3**), or the resolution of such a debt
(**C4**). The count at G5 is **fourteen**. **A marking may be scoped to an amendment** (ADR-0003 A2), and one
marking, ADR-0035 R2's, is by custodian instruction outside C1–C4.

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

**G checkpoint** [C]: the state of record. G5 (2026.09.29) is current. A cut is immutable, and corrections go to the
next one.

**Theory of Operation** [C]: the narrative. **It is not the state of record.** Rev 9 is current.

**Batch** [C]: a ratification group. Batches 10 and 11 were ratified on 09.28, Batches 12 to 16 on 09.29, and the
records tag them ⟨B10⟩ … ⟨B16⟩.

**Superseded** [C]: a status class since G5. The record keeps its accepted text, marked no longer in force, and names
the superseding record. ADR-0008 is the first.

**Run row** [C]: a History row of kind *Run* recording a ratification run's results on the record, before
ratification, with what it left outstanding on its face.

**Conventions** [C]: G-C1 (files are cited by digest) · **a tree is cited by manifest** plus commit · **drift pins**
(`mechanism/corpus-pins.sha256`) · **pointer errata** (a promised pointer, no decision text) · **dependent entries**
(a ratification row with no text change, inside the History table) · **one results file per run**, never
overwritten · **a frozen module's successor carries the amendment tag** · **a run finding the text disagrees with
is applied before ratification** · **placeholders say so three times**.

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
object** (ADR-0033 §1). It is cited by manifest and commit (last `SHA256SUMS-REF-2026.09.29` at `7f74c0b`), it has
never been promoted, and nothing in it is in any TCB. It issues only rung-0 leases, so it fails A1. **Twenty-five
assumptions and eighteen gaps** are tagged in the code (`GAPS-AND-ASSUMPTIONS.md`). Since 09.29 it has seat kinds,
cells, a correlator, heartbeats, marks, seals, coupling and coverage.

**Reference findings 1–11** [R]: routed to records in ToO §15. Three needed running code to find (1, 4 and 9). Only
finding 9, proposer retry in the drafted `Paxos` module, is still open (item 24). Three more on 09.29: one live lease
had been enforced per seat, not per principal; a coupling rule refused the heartbeat it depended on; `T_obs` cannot
be re-checked at apply.

**Host-run occupant** [R / P]: `serve.py` on the host with no container, the reference's first declared profile
(`slm/serve/profile-host-rung0.json`), a rung-0 principal whose `Mediated` verdict is derived rather than empty.

**Crash-recovery replicas** [A]: the consensus replicas are not Byzantine (ADR-0033 §3). **Replica authentication and
Byzantine replicas** are open (item 23). This is assumption A9.

**TCB declaration record** [O, 16]: it is unwritten. It is owed the engine-divergence and Byzantine-replica residuals.

---

## 10. Proposed records

Four records are Proposed at G5. **None is Accepted.**

**ADR-0005** [P, 5]: Kafka's role. The reference's use of Kafka is a debt against it.

**ADR-0021** [P, 4]: Build has an Observer. Blocked on ADR-0003's no-tiered-storage clause; R3 cites ADR-0038.

**Lineage projection** [P, 20]: ADR-0035 proposes that a Persona's lineage record is **projected from the Build log**,
not taken from the trainer's manifest. A lineage that can only be declared is **D-0035-1**. **Every share the gate
computes is an upper bound** (R2), after the rehearsal refuted the first draft's monotonicity claim.

**Exclusion rules E1–E5** [P]: two lineages are independent unless one of these fires: **E1** shared weights ·
**E2** shared generators · **E3** corpus overlap above θ · **E4** same architecture family and tokenizer · **E5**
shared curators. Plus the **distillation rule**. The rehearsal is in `slm/`; the θ values live in the values file
and are unset.

**Launcher** [P, 34]: ADR-0036. At rung 1 the launcher is the channel: **launch, appraise, grant, bridge**, with the
token never entering the guest. Its first profile fails P3. R1 adds the rung-0 declared profile and the ladder.

---

## 11. Outstanding

These terms name a hole. Each one points to the G5 §7 open list.

| Term | Item |
|---|---|
| **Sandbox gap** (mechanism half) | 1 |
| **Floor fitness** | 2 |
| ADR-0021 (Build Observer) · ADR-0005 (Kafka) | 4 · 5 |
| ADR-0017 supersession (the ADR-0008 half is done) | 6 · 50 |
| Archetype-evolution record | 7 |
| R8, break-glass TTL | 8 |
| Per-class floors (ADR-0014) | 9 |
| Re-genesis migration | 10 |
| Custody beyond (1, 0) | 11 |
| Run's alphabet, and Run's `R` | 13 |
| Solver trust for routing's "implies" results | 15 |
| TCB declaration record | 16 |
| Decoder–alphabet compatibility; a decoder seat | 17 |
| **Bundle signing** | 18 |
| Independence criterion · Persona expiry | 20 · 21 |
| Lifting a revocation | 22 |
| Replica authentication | 23 |
| Finding 9 | 24 |
| Genesis floor, S and the values, DRAFT | 25 |
| The Run profile · verifier key · retention · accelerator attestation | 26 · 27 · 28 · 29 |
| θ values · best-practice review of the bound | 30 · 33 |
| ADR-0036's run · the launcher in the node · a P3-passing image | 34 · 35 · 36 |
| ADR-0026 §6 rerun with A2.2 and A2.3 | 39 |
| **Properties lost** field | 40 |
| **Seat-registration record** | 41 |
| ADR-0037's occupant steps (retention audit, Reader facts) | 42 |
| **Correlator's detection function** | 43 |
| Sequence numbers on denials · correlator's store vs erasure | 44 |
| A scripted cell Observer | 45 |
| `W(p)` as an ACL · gate-side `K < R` · A2.2 in the reference (G18) | 46 |
| **Measured `T_obs`, `K`, Run's `R`** | 47 |
| **Quarantine gate** · Observer round layout | 48 |
| Break-glass under a dead Observer | 49 |
| **Delegation / on-behalf-of** · attenuation · honeypots | 51 |
| The live smoke run | 52 |

Unowned and not numbered: **`Invoke` hermeticity** for native tools · **flow** (CR-6) · the **residual-risk
statement**, headed by anchor capture and now carrying collusion.

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
5. **"G" and a number: checkpoints, conventions and gaps.** G1–G5 are checkpoints, **G-C1** is a convention, and
   **G1–G18** in `mechanism/` are code gaps: *G5* is now both a checkpoint and a gap. Name the three floor gates;
   don't letter them.
6. **"Rung": now three orderings.** ADR-0023 degeneracy rungs (per axis), confinement attestation rungs 0–3
   (ADR-0034, Accepted), and provenance rungs on ADR-0017's axis. `slm/` says "every round runs at rung 0", meaning
   **attestation** rung. Always qualify.
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
16. **"Confirmation-required" count.** G5 and rev 9 say **fourteen**, three of them for one amendment only; the
    09.26 glossary's *nine* was G3's.
17. **"Seat": two senses, one word.** The LTRO position (ADR-0016, ADR-0037) and the promotion-roster slot
    (ADR-0024). The **kind** field separates them; an Observer holds both at once.
18. **"R": four uses.** Rules-floor entries, record revisions, the readiness key, and now the **round bound** `R`
    (ADR-0022 §3, ADR-0039 §1). "`K < R`" is the fourth.
19. **"Declared": a fourth sense.** A rung-0 **declared profile** (ADR-0036 R1): declared by the operator, verified by
    nobody. Results print the word so it is not mistaken for attestation.
20. **"Coverage" and "live" are two different facts.** Coverage is a watermark at the seal; live is a fresh heartbeat
    with a watermark within `K`. A promotion needs the first; a Run admit needs the second.
21. **"Reader" is no longer a seat.** Text that gives the Reader a Persona, a lease or a distinctness obligation is
    pre-ADR-0037.

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
| Monotonicity "at five layers" | Twelve layers | ToO rev 9 §7.8 |
| "Principals are agent LTROs"; the LTRO as one principal | An LTRO is a cell of principals; a principal holds one seat | ADR-0037 §1 |
| The Reader as a cognitive seat with its own Persona | A stage producing facts for the cell Observer | ADR-0037 §3; ADR-0018 B12 |
| "Human principals are atomic", as a contrast | Every principal is atomic; a human holds one seat | ADR-0037 §7 |
| The shared, orchestrator-level Observer group (~9 vs ~40 instances) | One `observer` seat per cell plus a correlator; any-of | ADR-0038 §1, §5; ADR-0008 superseded |
| "A Byzantine quorum of co-resident replicas is arithmetic fiction" as the placement reason | Correlated failure and a device-memory effect path; there is no Observer quorum | ADR-0038 §4, §5 |
| Veto seats held by "the independent Observer replicated group" | Every cell Observer and correlator seat in Build | ADR-0024 A2.1 |
| "An unavailable Observer vetoes nothing" as the accepted state | An absent Observer stalls: coverage and an independent veto seat are tally constants | ADR-0024 A2.2, A2.3; ADR-0039 §3 |
| Detection fails open, unstated | Coupled in Run and at the Build gate; fails open against collusion only, declared | ADR-0039 |
| `seq − mark ≤ K` | `seq − mark < K`, the strict form | ADR-0039 §1 R5 |
| R3 on every uncovered Run emission | R3 under a `thinker` seat only | ADR-0039 §2 R5 |
| "The rung-0 verdict is computed from nothing" | A rung-0 grant may name a profile; the verdict is then derived, and *declared* | ADR-0036 R1 |
| The floor as two files | Three: policies, schema S, the values file | ADR-0039 §1 R3 |
| "Renewal may lower the rung" | Renewal keeps the rung | ADR-0031 A1 |
| The cross-principal correlator as "a noun" | A seat kind, a placement, a veto seat and a read set; still no detection function | ADR-0038; G5 item 43 |

---

## Sources

**Basis.** `checkpoints/topak-genesis-checkpoint-G5-2026.09.29.md` · `checkpoints/topak-theory-of-operation-2026.09.29-rev9.md`
· the records they cite, at their G5 digests.

**Superseded.** `derived/topak-glossary-2026.09.26.md`, and through it the 09.17 glossary whose §12 is carried by
reference.
