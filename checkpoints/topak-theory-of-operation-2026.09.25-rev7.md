# TOPAK — Theory of Operation

**2026.09.25** · revision 7 · **narrative only** · cut from Genesis Checkpoint G3 · supersedes revision 6 as narrative

Revision 7 is revision 6 corrected against G3. Between the cuts four records were written — the floor language
(ADR-0030), the lease (ADR-0031), the clock model (ADR-0032) and the reference implementation (ADR-0033) — the admit
path was built and run, and its eleven findings changed five records. Passages those changes made false are
rewritten; the narrative spine, examples, and framing are revision 6's. Section numbers are kept, because records
cite them: the lease enters as §2.5 and the reference as §15. Appendix C lists every change.

---

## 0. How to read this

**This document explains how the design fits together. It is not the state of record.** Status, readiness,
digests, the ratification queue, the genesis debt ledger, and the open list are in **G3**.

The narrative describes what the records say. Status words appear only where status changes the meaning — a
reversal in effect, a claim still carrying a confirmation marker, or a section of a record that was deliberately
left unratified.

**What "ratified" means here, and what it does not.** Twenty-nine records are now Accepted (genesis). Nine of them
carry a confirmation-required marker — one, ADR-0003, for a single amendment only — which means they were ratified by
one person and must pass an independent confirmation promotion after bootstrap. **Until then, any claim resting on
those nine is author-ratified, and this document says so at each point rather than once in a footnote.**
Ratification by a sole custodian is a declaration, not a review.

**Findings.** Revision 5 carried ⟨S6-n⟩ markers where records disagreed. All are dispositioned; §14 lists each with
its outcome. Markers that remain in this text point to findings from the 09.16 critical review and the 09.17
narrative log that are open, not to corpus contradictions.

---

## 1. The pattern

TOPAK is an architecture pattern for autonomous multi-agent collaboration that is safe by design. The letters
name its five components:
- **T**, TLA+ (Temporal Logic of Actions): the formal specification and model checking;
- **O**, policy as code: a verified floor evaluator and a per-request bundle engine — Cedar and Open Policy Agent
  (OPA) with Rego at the reference;
- **P**, Paxos: consensus over the control plane;
- **A**, agents: the principals doing the work;
- **K**, Kafka: the event transport.

**The letters name roles, not products** (ADR-0030 §2, ADR-0033 §2). Each role carries a stated obligation, and an
instrument that meets it may be substituted. The O is where this matters first: its floor tier needs an evaluator
with a mechanized semantics and decidable policy comparison, which Rego does not have and Cedar does (§3.1).

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
operational bundles and on the floor itself (ADR-0007 extension, from ADR-0010). On the floor they are now
**decidable checks** with proof-backed answers — never-errors, not always-allows, not always-denies, per action over
schema S — and a failing check returns a counterexample request (ADR-0030 §5). Some desirable policies become
inexpressible at admit time and have to be restated as detections. That is the price of keeping models out of the
TCB.

### 2.3 `Contained` and `Mediated`

`Contained(p)` holds when a principal reaches the world only through its alphabet. A principal with a shell, a
package manager, network egress, or a git remote is `Mediated`: effects exist that no action names, so the
alphabet is not total. Safety theorems quantify over `Contained` principals. For `Mediated` principals the
architecture offers attribution and authorization, not containment.

**Confinement is carried in the lease** as a profile digest and an attestation rung (ADR-0031 §3, §2.5 below).
**Rung 0 is `Mediated`, always.** A higher rung is necessary for `Contained` and not sufficient: the provenance axis
must also clear, and the criterion for it is unwritten, so `Contained` is unreachable at every rung today.

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
- **Finite in variants, not in instances.** `Read` ranges over a large ground set, so the floor is analysed per
  action variant with symbolic parameters — Cedar's analyses over schema S (ADR-0030 §5) — not by enumeration.
  Earlier revisions said Rego predicates checked by an SMT solver; that needed a mechanized Rego semantics nobody has,
  and ADR-0030 retired it.
- **`Invoke` is the whole attack surface.** One allowlisted tool with a socket collapses the envelope to vacuity.
  Each allowlist entry carries a hermeticity obligation; nobody owns it yet.
- **Seat separation.** Per artifact, the author and the voters are disjoint, and a voter in a promotion round
  cannot `Draft`, `Invoke`, or `Submit`. **Recusal lives here and only here:** the `Vote` envelope refuses an
  author's vote, which makes it no issued value, and is why rules-floor entry R3 was withdrawn as vacuous (§7.3).
  **The envelope is floor text** — forbid B7 in the policy floor (ADR-0030) — so relaxing recusal is a policy-floor
  relaxation: an anchor issuance and a promotion (ADR-0022 A1). Revision 6 said a mechanism release; the floor path
  is stricter, and the same holds for every envelope constraint the floor states. No declared degeneracy asks for
  any of them.
- **The anchor's actions are not Build actions.** `Issue` and `Resign` are environment events no Build principal can
  express. Resignation now has a meaning on each custody rung: at archetype custody it is a permanent loss and
  freezes the rules; under a threshold rung the recovery rule rotates the key; under n−1 eviction it consumes that
  epoch's single eviction (ADR-0025 annex).

**Confinement is an obligation, not an assumption** (ADR-0022 §6): no shell, no network egress, no filesystem
outside workspace and corpus, no path to the artifactory except `Submit`. It is stated and not discharged. Until a
mechanism enforces it, **Build principals are `Mediated`**, and every Build containment theorem is conditional on
it. While this *sandbox gap* stands, `Contained` may have no members at all.

**Capability cost.** This is not how agents write code today: no shell, no package installation, no network, no
git. The article has to say so before a reader who has used a coding harness says it for us.

**The alphabet is the agent's interface at the reference.** The six variants are exposed as MCP tools and nothing
else, on a front door the mechanism owns (ADR-0033 §2). That makes the alphabet the whole *protocol*. It does not
make it the whole *channel*: an agent process with a shell never has to ask. The reference is the plainest
illustration of the sandbox gap there is.

### 2.5 The lease is the credential

Every action carries epoch and lease (§2.4). ADR-0031 says what the lease is: **one composite credential, granted
for one round, with a closed schema** of twelve fields — principal, seat, Persona, epoch, fence, rules epoch,
bundle, confinement, alphabet, round, role, and TTL. Every field is an authority claim, and a capability that is
not a field is not carried.

- **The lease is round-coterminous, and a principal holds at most one live lease.** A grant requires that none is
  live. Without that rule, monotone renewal guarantees nothing, because a principal wanting wider authority simply
  takes a fresh grant; the property check found exactly that on its first run.
- **The fence is the Paxos log index at grant**, not a counter of its own, so leases, admits and issuances are
  ordered by one log.
- **Renewal only narrows.** It may narrow the alphabet, lower the rung or shorten the TTL. It keeps the bundle, the
  round and the role: none of the three is ordered, so a change of any of them is a grant. Keeping the bundle means
  a bundle promoted mid-round reaches a principal only at its next grant — **tightening a live round ends it**.
- **Revocation has two tools.** A *targeted revocation* ends the leases matching a principal, a Persona or a
  confinement profile, bars later grants to it, and lapses the seat's break-glass approvals; nothing else stops. An
  *epoch fence* ends every live round, and is kept for e-stop and for scopes nobody can name. Earlier text had only
  the fence, which made revoking one principal a fleet-wide reset. Both are ordered, neither needs a quorum, and a
  revocation is permanent within the chain.
- **Expiry is local and then ordered.** A replica reads its own monotonic clock, with a margin that errs toward
  early, and the first to see expiry proposes the round's end as a log entry, so every replica agrees when the slot
  frees (ADR-0031 E1).
- **The field list is the per-round TCB.** Persona, confinement, bundle, alphabet, round and role are checked at
  grant and assumed for the round; epoch, fence and rules epoch are compared on every action.

**Author-ratified.** ADR-0031 is confirmation-required under C1, for the break-glass lapse on revocation.

---

## 3. Policy

### 3.1 The verified object and the policy floor

Moon & Varshney put boundary policy inside the verified artifact. TOPAK externalizes it into signed bundles that
change at runtime, and bounds them (ADR-0010).

**The verified object** is the enforcement mechanism, its version pinning, its epoch fencing, a **minimal policy
floor**, and (per ADR-0010 A1) a **minimal rules floor** (§7.3). Operational bundles are versioned parameters. They
may subtract authority, never add it.

**Refinement is a property of composition, not of the bundle** (ADR-0030 §1). For every admit decision, over one
frozen input,

> **admit ⟺ floor_permit ∧ ¬bundle_deny**

- **`floor_permit`** holds only when the floor returns Allow with no evaluation error. Cedar skips a policy that
  errors, so an erroring `forbid` would not fire; any error is therefore a deny.
- **`bundle_deny`** holds unless the bundle affirmatively allows — a deny, an error, undefined, absent, or unreachable
  are all refusals. A bundle is never asked whether to grant.
- **A bundle decision counts only from the revision the lease names.** Where the tier runs a sidecar and a local
  engine, the local engine decides only when the sidecar cannot answer and it holds that revision; otherwise the
  bundle is unreachable and refuses. Without the binding, a sidecar outage would lift every narrowing pushed since
  the local copy was built.
- **A floor deny names its reason**: the forbids that fired, or *no permit matched*. Without the second case most
  denials would answer "why?" with nothing.

So `bundle ⊑ floor` holds of the composed decision for **every** bundle at **every** age: it is no longer something a
bundle can fail, and nobody has to decide it at promotion. What that buys:
a - **Containment is checked against the floor** and no bundle can weaken it.
- **Stale bundles are monotone-safe**, now with no refinement premise at all. Local enforcement under partition
  (EL zone 1) survives, sound by construction rather than operational care. This is the same shape as the lease
  argument.
- **No cross-language check.** Earlier revisions decided refinement at promotion with an SMT solver over Rego. That
  check needed a mechanized Rego semantics and an analyzer proven against it; composition removes the need.

**What is given up.** A bundle cannot establish that something is allowed. Over-denial by a bundle is a modeled,
attributed local event, and a bad bundle can disable break-glass — a liveness cost, never a widening.

**The floor runs on a verified evaluator, linked into the mechanism** (ADR-0030 §2, §3). The floor tier's obligation
is an evaluator with a mechanized semantics, an implementation checked against it, and a decidable comparison of
two policy sets. Cedar meets it; the reference links the Rust engine, whose chain to the Lean model is shortest. The
bundle tier stays OPA and Rego, because deployments already run it. The floor is a library, not a service — no
process, no socket, no fetch — and its only inputs come from the typed lift and the issued rules, so no bundle can
write a value the floor reads. **Schema S** is the lift's type and is enforced on every request; an analysis about a
schema the running system does not enforce proves nothing about it (ADR-0030 §4).

**Nothing translates.** Neither Rego → Cedar nor the reverse is in the archetype: a transpiler is a Build artifact
whose output becomes the enforced floor, and a silent mistranslation is exactly the failure this is meant to rule
out (ADR-0030 §6). A deployment that keeps a Rego floor declares **D-0030-1**: floor non-vacuity and revision
classification become measured rather than proven. `bundle ⊑ floor` survives it, because composition does not
depend on the floor's language.

**The genesis floor exists, as a draft.** Fourteen Cedar policies and schema S, gated on 2026.09.24: every policy
never errors on every action it covers, every action is neither always-allowed nor always-denied, removing any one
policy changes the floor, and three deliberately broken controls were caught. The text is **not ratified**; ADR-0030
ratified the language and the machinery, not a floor.

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
| A revision that is neither tighter nor looser | **Routed as a relaxation**: an anchor issuance and a promotion |
| Any change to the rules floor | An anchor issuance **and** a promotion |

**The classification is computed, not asserted** (ADR-0030 §5). Between the deployed floor F and a candidate F′, the
analyzer decides `F′ ⇒ F` and `F ⇒ F′`, and the answer picks the row. A Build author — Byzantine by premise — cannot
relabel a relaxation as a tightening to choose a cheaper authority path for its own change. The analysis results go
into the gate evidence that votes already bind to.

The policy floor ships inside the mechanism, and mechanism releases are promoted like any artifact (ADR-0024 §1).
Earlier text described the floor as "the one artifact verified rather than promoted." Both are true in sequence:
the floor is verified with the mechanism, and the release carrying it is promoted. The only artifact that is
never promoted is the genesis bundle (§9). The older phrasing survives in two records' consequences and was left
there deliberately: their decision text stays true, and the amendment test changes a record only where its decision
becomes false.

### 3.3 Exceptions

Two privileged paths cannot be written as subtractions. **Erasure** (ADR-0006) destroys authority-bearing
evidence. **Break-glass** (ADR-0009) adds authority. Both are **floor exceptions**: carve-outs inside the verified
object, each with a quorum predicate checked in TLA+.

ADR-0013 writes the exception mechanism once:
- **Exceptions are declared floor entries**, each with an envelope, a roster reference, and non-composition
  obligations. Adding one is a floor relaxation. Since ADR-0030 they are **Cedar policies inside the floor**, as are
  the six forensic classes, so composition applies to them uniformly: **a bundle can narrow a floor exception,
  including break-glass**, and cannot widen either.
- **The exception count is bounded** by rules-floor entry R6. The current count is two.
- **Non-composition** is stated as TLA+ invariants with mutations, and both were **checked on 2026.09.23**
  (`spec/NonComposition.tla`). **NC-1:** break-glass chained with erasure never yields an effect that is authorized,
  erased, and unattributable. **NC-2:** erasure never removes a forensic-floor record under any composition with
  break-glass. Both hold under the mechanism as the records specify it; both fail under a mechanism that lets
  erasure reach admit decisions, or that lets a break-glass grant widen the erasure envelope. A third witness shows
  the composition is reachable at all — without it NC-1 could hold because the two privileged paths never meet.
- **Privileged grants share one authorization model:** a quorum on an anchor-issued roster, bounded by the rules
  floor. **Privileged** is load-bearing: ordinary Run admits are grants too, and they are decided against a bundle,
  not a roster.
- **Demand type 5 is declined.** "Hide that a record ever existed" conflicts with NC-2, because the erasure event is
  itself a forensic class. The archetype does not support it, and compartmentation — narrowing the reader set while
  the audit authority still reads — is not the same thing. A deployment needing type 5 in full is outside the
  archetype's declared demands.

Every carve-out works against floor minimality. That tension is why the count is bounded.

**Author-ratified.** ADR-0013 and ADR-0028 were ratified in genesis on 2026.09.23, both confirmation-required under
C1, and ADR-0030, which re-expresses both as floor entries, on 2026.09.25 under the same criterion. The checks above were run by the author, and they are evidence, not attestation. The record itself says the
phase move gave up the independent reviewer that the post-bootstrap phase would have supplied.

### 3.4 One floor or one per class?

ADR-0010 specifies one floor shared by Build and Run. ADR-0022 shows the two domains have partially disjoint
alphabets, so a single floor is either vacuous on the variants a domain lacks, or two floors under one name. The
evidence points to **per-class floors sharing a verified core**. The same question now applies to the rules floor.
It is unresolved. Cedar scopes policies per action, so either answer can be stated in the floor language; ADR-0030
deliberately does not choose.

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

> effect → admit → floor ∧ bundle, at the lease's bundle revision → rules epoch → issuance → ADR-0025's intent axiom

and no link is assumed except the last. **Denials are not ordered:** a denied effect never crosses the boundary,
and absence of effect is not an event.

**Deciding and ordering are separated in time** (ADR-0033 §4, to which ADR-0015 now points). An admit decided under
epoch *e* can commit after a revocation has moved the epoch on. So the mechanism checks run twice — before the floor
is consulted, and again at the entry's log position when it is applied — and an admit that fails the second run is
**void**: ordered, recorded, without effect. The floor and bundle are not re-run; their decision is recorded with the
digest of the frozen input it covers. The effect runs only after commit, and a crash between commit and effect
leaves no effect, which is safe.

**Ordering is not authorization.** Revocation, expiry, abstention and the end of a round subtract authority, so they
need no quorum — but they change replicated state, so they must be ordered, or replicas disagree about what is live.
The corpus had used the two properties as one; the reference could not run until they were separated.

**Denials are not ordered, and they are recorded** (ADR-0020). "Actions attempted, including those denied" is part
of a round's replayable record: without them the trail shows a clean system and cannot tell *behaved* from *was
prevented*. ADR-0020 named this the clause an implementer optimizing topic volume is most likely to drop, and the
reference dropped it; review caught it (§15). A denial is written, unordered, to the principal's round topic by the
replica that decided it, with content reduced to digests.

**Break-glass and erasure are not a third kind.** Each is invoked as an admit decision against its declared
floor-exception entry, so both are already effects. Break-glass grants authority *within* the rules in force and
cannot alter them, because no break-glass grant may authorize `Issue`, `Vote`, or promotion (R7). The qualifier
that keeps the authority-change set at two is therefore **change to the rules in force**, not "adds authority".
That classification rests on the exception entries of ADR-0013, which is itself confirmation-required.

This makes **effect exclusivity a mechanism claim**, which is strictly stronger than Moon & Varshney's assumed
version and TOPAK's sharpest differentiation. It is also entirely contingent on the sandbox gap. Any sideways
effect path falsifies the enumeration rather than degrading it.

### 4.2 What Kafka is

Kafka is **neither the ordering authority nor the system of record** (ADR-0005). It is a transport with a
durability window (`acks=all`). The causal frame comes from the Paxos log. The archive is the system of record.
An emission is written only after its admit commits, and carries the admit's log index, the lease fence and a
per-lease sequence number.

ADR-0015 shrinks the remaining ordering problem to one residual: effects admitted in the same round but emitted at
different times. The per-lease sequence number covers it at the reference. If the Observer's quarantine gate is a
modeled event, the residual closes entirely. That question gates ADR-0005, which is still Proposed — and the
reference's choice of Kafka is carried as a debt against it (ADR-0033 §2).

### 4.3 Topics, payloads, erasure

**Topics.** One topic per principal per epoch or round, sealed on emit completion, with per-topic access control,
per-use-case retention, explicit replay authorization, write-time masking by wrapper Rego, and no tiered storage
(ADR-0003). The **topic is the unit of erasure**. Deleting a sealed container never edits a signature or a hash
chain, and a masking miss has a blast radius of one round. The cost is topic count, principals × rounds.

**Two amendments, both from running code** (ADR-0003 A1, A2).
- **A topic's identity includes its rules-epoch chain.** Re-genesis restarts epochs and rounds at zero, so without
  the chain a successor's first round names its predecessor's — shown live when two development resets wrote into
  the same Kafka topic. A sealed topic must never be written again, so the chain is part of the name.
- **A round has one companion topic, `after`**, for denials under the round's lease once its topic is sealed: a
  principal whose round was submitted, expired, revoked or fenced, still holding its token and still trying. After a
  revocation, that is the most valuable evidence the round has, and under the unamended text it had nowhere to go.
  The companion carries denials only, belongs to the same subject and round, and is erased with it. It is bounded:
  past a limit, one marker records that attempts continued, so a misbehaving agent cannot turn its own revocation
  into an unbounded write. **Author-ratified**: A2 is confirmation-required under C1, the only marking in the corpus
  scoped to one amendment.

Crypto-shredding was considered and rejected: it leaves a verifying envelope over unreadable ciphertext, a hole no
auditor can tell from suppression. Three documents said the opposite as recently as 2026.09.15; the records are
corrected, and the derived documents are still to be regenerated.

**Control-plane facts and payloads.** Trace conformance needs actions, identities, and ordering, not prompt text.
Forensics needs the text. In the archive, the control-plane record keeps a hash and a pointer, and plaintext lives
in a separately governed store built for deletion (ADR-0004).

**Erasure is a modeled event** (ADR-0006): consensus-ordered, modeled in TLA+, recorded in the log it modifies. Its
authorization predicate lives in the verified object, not in a bundle. Its mechanism is deletion of sealed topics
and of plaintext-store entries. The spec obligation is a safety property that separates lawful erasure from history
rewriting.

**Replay reconstructs what crossed the membrane**, not what happened inside it (ADR-0020) — including the attempts
that were refused (§4.1). The Observer and replay read the same stream, so an investigator can never be shown
something the Observer lacked at detection time. That keeps detection latency `L` an honest number.

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

**Where a vote actually lives.** The authoritative vote is the admit decision in the consensus log, which is what
F3 retains. The voter's round-topic emission carries the vote together with a hash-and-pointer to its commentary in
the separately governed store; the commentary is what erasure removes. Without that split the record contradicts
itself: the sealed topic is the unit of erasure, so a topic holding both a vote and its commentary is either
erasable as a unit, losing F3, or permanently unerasable, losing the erasability of commentary. Neither the topic
nor the emission is the record; the log is.

**One seam remains.** The horizon is the lifetime of the rules-epoch chain, and re-genesis starts a new chain — so
the authority record lapses exactly when it matters most, since re-genesis follows anchor loss or capture. The rule
that a successor inherits read access to its predecessor's forensic classes is carried as a re-genesis migration
obligation and must be settled before ADR-0028's confirmation promotion. ADR-0003 A1 removes one precondition — a
successor can now tell its topics from its predecessor's — and settles nothing else.

**Stop attribution is non-erasable because it is a feedback path, not just evidence.** In system-theoretic terms
(STPA), the Observer is a controller, not a probe.

**At bootstrap, genesis rules issue no erasure roster.** Both records were ratified on 2026.09.23, and that does
not change the position: the roster is withheld by the ceremony itself, not by either record's status. Erasure is
therefore disabled from epoch 0, and the first erasure roster is issued after bootstrap under the two-key rule, by
which point both records have been through confirmation. This is fail-closed and costs nothing, since there is
nothing to erase yet — but it does mean ADR-0006 stands ratified with no path to exercise it until then.

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
not independence of judgment. The accepted text stays in force until a superseding record exists, and **that
record has not been written.** It also has to name who holds promotion veto seats: ADR-0024 assigns them to the
shared Observer group, which is the scoping being reversed, and the correlator is the natural candidate. Because
ADR-0024 is a bootstrap record that can carry no confirmation marker, changing the veto-seat holder later reaches a
bootstrap record through an ordinary promotion.

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

**Timing runs the right way.** Run's budget is hard: the propagation window `W` is about a second and no human fits
inside it, so Run is human-on-the-loop (HOTL). Build favors consistency over latency and its promotion
gate blocks, so Build detection only has to finish before the gate clears. Detection is cheaper in Build, which
makes its absence harder to defend. ADR-0021 is corrected for quorum promotion — every vote covers the artifact
digest and the sealed topic-set digest, and the grant seats authorize, not a human key — but it stays Proposed:
its long Build retention conflicts with an accepted clause on tiered storage, and that is a decision to take
deliberately rather than as a side effect.

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
exception: revocation, decoder failure, and subtraction are all denies. The Persona is a lease field (§2.5), so a
revoked Persona is a targeted revocation: its leases end, it is barred from later grants, and no other round stops.

---

## 7. Authority

### 7.1 Promotion is a quorum grant

The single promotion signing key was the last privileged human grant. ADR-0024 replaces it.

- **Promotion is a grant.** Everything crossing from Build to Run is promoted: bundles, mechanism releases
  (including floor changes), and Personas.
- **The quorum rule is read from issued rules.** `quorum` is either `"all"` or a grant-vote threshold *k*. At the
  archetype it is `"all"`: every counted grant seat must grant, and a grant-seat deny or abstention denies. **A
  timeout is never a grant**, as a mechanism constant. The earlier `"any"` value is withdrawn — it is *k* = 1, which
  tolerates no Byzantine approver and was never the k-of-n degeneracy it appeared to be.
- **Seat classes.** *Grant seats* are human `Mediated` principals with named organizational roles. *Veto seats* are
  held by the independent Observer and can only deny. Under unanimity every seat is a veto; a veto seat is one whose
  alphabet lacks `grant`.
- **Veto-seat silence is not a veto.** Requiring an Observer "no finding" attestation would make semantic judgment an
  enabling condition, which ADR-0007 forbids.
- **Votes bind to (artifact digest, gate-evidence digest, rules epoch).** Any rules-epoch change voids in-flight
  votes: fencing, the same shape as leases.
- **Gates enable voting; they do not vote.** `Vote` is enabled only after the ADR-0007 gates pass. `bundle ⊑ floor`
  no longer needs checking here, because composition makes it hold for every bundle (§3.1).
- **The author is recused**, as a mechanism constant rather than an issued value: the author is removed from the
  counted seats, and the `Vote` envelope refuses the vote itself (§2.4). If recusal leaves fewer seats than the
  floor minimum, promotion is denied.
- **Runtime subtraction is not promotion.** E-stop, lease expiry, revocation and `deny=all` need no quorum and are
  attributed. Where they change replicated state they are still ordered (§4.1).

Promotion now obeys consensus-for-grants like every other grant, and no strict subset of grant seats can promote.
Two costs are stated in the record. **Liveness equals the availability of every grant seat.** **Correlated review
failure is untouched:** unanimous humans reading the same vacuous gate output fail together (Moon & Varshney §4.6;
Knight & Leveson). Floor fitness, a fourth gate (NIST MEASURE 2.13), is still unowned.

**A promotion is a round**, keyed by artifact digest. It does not depend on the Build effect-stream scheme: what
promotion requires is the vote record in the consensus log (§4.4), which is not a property of any topic scheme. A
bootstrap record therefore rests on nothing that is still unratified.

**Author-ratified.** ADR-0024 is Accepted (genesis) without a confirmation marker, because the bootstrap set cannot
carry one — confirmation runs under this record, and confirming it under itself would be circular. Its safety rests
on the genesis attestation and the intent axiom, never on independent review. That is the sharpest instance of
§9's weakest point.

### 7.2 The trust anchor is a havoc issuer

Promotion moves the gate up one level: the authority defining who votes cannot itself be voted in without regress.
ADR-0025 weighed three treatments of that authority, the **trust anchor**: infallible (an oracle), havoc (any
authentic issuance, bounded by a verified floor), or characterized (havoc plus a model of how members decide).

Under havoc, safety must hold for every issuance the anchor could make, so the anchor's composition never enters
the proof. The decision is **havoc, with "infallible" split three ways**:

| Property | Treatment |
|---|---|
| **Intent** | **Assumed**, the sole axiom: *an authentic issuance at the current anchor epoch is what the anchor intended.* |
| **Integrity** | **Modeled**: `Issue` is an environment action bounded by an opaque `Authentic`, epoch increment, and the rules floor |
| **Custody** | **Declared** per deployment position: the pair (capture threshold, loss tolerance) |

**Rules** are the authority-defining set: the promotion roster and its parameters, the break-glass and erasure
rosters, the anchor's own key set, any relaxation of the policy floor or new exception, and **any change to the
rules floor in either direction**. Tightening the *policy* floor is not a rules change — it is an ordinary
promotion. The rules floor is the exception, because tightening it constrains the anchor itself, so the anchor must
consent (§7.3).

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
| R3 | *Withdrawn*: recusal is enforced by the `Vote` envelope, so no issued value exists to bound |
| R4 | *Withdrawn*: a timeout never grants, now a mechanism constant |
| R5 | No key both in the anchor key set and on the promotion roster |
| R6 | Exception-count bound, currently two — **effective 2026.09.23** with ADR-0013 |
| R7 | No break-glass grant may authorize `Issue`, `Vote`, or promotion |
| R9 | `quorum = "all"` or `quorum ≥ 2` — a **conditional entry**, binding only once R1 is relaxed |
| R8 | *Drafted*, pending (ADR-0026 A1): a break-glass grant TTL. Vacuous until a mechanism clause makes a grant end, and by ADR-0032 it needs trusted time |

**Why R9 exists.** Relaxing R1 alone yields a threshold *k*, and without R9 that threshold may be 1 — single-signer
promotion entering as though it were k-of-n. R9 keeps the two declared degeneracies distinct. It is the corpus's
first entry that bounds *degeneracies* rather than the archetype, and it does not pass the independence test as
that test is written: every rule set R9 excludes is also excluded by R1. Its independence is stated relative to a
floor without R1, which is the only situation in which it binds.

**Parametricity is load-bearing, and so is its converse.** A floor entry bounds something only if the mechanism
reads that value from issued rules; a value the mechanism fixes as a constant cannot be bounded by a floor entry at
all. Two runs establish both halves.

The 2026.09.15 run (`RulesFloorNV`) showed the first:
- Against ADR-0024 revision 3, which hard-coded the values, R1–R3 constrained nothing.
- **Dropping R2 promotes with zero votes.** A havoc issuance sets an empty roster, and unanimity over the empty set is
  vacuously true. R1 alone does not protect against an empty roster.

The 2026.09.23 rerun (`RulesFloorNV_rev5`) checked the mechanism as it now stands, and modeled the `Vote` envelope
for the first time. Every entry has a mutation that fails, promotion is reachable, and all six properties hold. It
returned two results the drafting did not anticipate:
- **R9's independence is conditional**, as above.
- **The earlier model was too small to check R1 once `quorum` became a threshold.** With four humans, the anchor
  key-holder is off the roster and the author is recused, leaving exactly two counted seats — and a threshold of
  *k* ≥ 2 over two seats *is* unanimity, so dropping R1 changed nothing and the mutation held vacuously. Five
  humans fixes it, which is independently the archetype headcount (§9). **A threshold mechanism needs at least
  three counted seats before any threshold property means anything.**

Withdrawing R3 is safe on evidence rather than on argument: with recusal removed from both the counted seats and
the `Vote` envelope, the author self-grants and the property fails.

**Two keys, both directions.** A rules-floor change needs an anchor issuance and a promotion under the rules being
replaced. Tightening needs both too, because a tightened rules floor constrains the anchor, which must consent. That
is where the rules floor differs from the policy floor.

### 7.4 Genesis rules are resident

At cold start or under partition the anchor may be unreachable. If genesis rules were fetched, every grant path
would block. ADR-0027 applies ADR-0012's argument to rules: **genesis rules ship with the mechanism release and are
fetched from nowhere.** Anchor unavailability blocks change, never operation. Epoch 0 is the root of the rules-epoch
chain.

**How the genesis floor check actually happens.** At epoch 0 there is no roster to promote under except the one the
genesis rules themselves define, and the genesis bundle is the only artifact never promoted. The check is therefore
the `GenesisSatisfiesFloor` invariant in the bootstrap specification, not a promotion; a later mechanism release
carrying resident rules is checked at its promotion, as normal. **An admitted issuance is persisted with the same
residency as genesis rules** — without that, "the last resident rules" would name nothing after epoch 0.

The cost is stated: a compromised genesis is a compromised system, covered only by the intent axiom.

### 7.5 Who is at the gate

- **At archetype custody,** anchor key-holders are removable only with their own consent, so they sit at the gate.
  They are attributable non-principals; `Mediated` applies to them as attribution only.
- **At degenerate custody,** the genesis threshold or eviction rule can remove a key-holder, so key-holders become
  principals and the gate moves to that rule. That is a type change, and it moves the TCB (§8.2).
- **Promotion voters are principals on every rung**, because the anchor can evict them. Promotion therefore enters
  `Build(Contain)` enforcement coverage.

ADR-0002's amendment, ratified 2026.09.23, carries the custody qualifier: *at archetype custody, the anchor's
key-holders are at the gate.* The unqualified sentence would have made an archetype-only claim on every deployment,
in a record that is rung-agnostic.

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

### 7.8 Monotonicity, layer by layer

| Layer | Statement | Source |
|---|---|---|
| Decision | Consensus for grants, local for denials | Established |
| Policy | Bundles only subtract from the floor — by composition, for every bundle | ADR-0010, ADR-0030 |
| Change | Authority-increasing changes need consensus; decreasing ones need no quorum, are attributed, and are ordered when they change replicated state | Floor-rollout session; ADR-0033 §4 |
| Deployment | Degenerate forms lose theorems, never gain capability | ADR-0023 |
| Authority | Relaxing rules needs the anchor; operating within them does not | ADR-0025, ADR-0026 |
| Evidence | Authority facts survive erasure and break-glass | ADR-0028 |
| Credential | Renewal only narrows; widening needs a fresh grant after the round ends | ADR-0031 |
| Time | An interval whose failure subtracts may use a local clock; one whose failure preserves authority needs trusted time | ADR-0032 |

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
- **Admission also checks type changes.** Reachability by parameter limit is necessary, not sufficient. A variation
  that moves a participant's *type* — anchor key-holders becoming principals under a degenerate custody rung, for
  instance — can void **no theorem at all** while moving what the theorems are about. Premise loss does not see
  that, so the type change is declared and checked at the same gate.
- **Every degeneracy carries a declaration record** with a fixed schema: **kind**, parameter, archetype value,
  deployed value, premises falsified, theorems voided, **type changes**, optional mitigation, and a composition note
  above one parameter.
- **Kind** is one of two. A **mechanism degeneracy** changes a value inside the verified object and reopens the
  proofs that quantify over it, shipping as a mechanism release. A **declaration degeneracy** changes something
  outside it and reopens nothing. That field is what makes "a promotion degeneracy is a mechanism release, an anchor
  degeneracy is a declaration" checkable rather than asserted.
- **Composition is owned here, and the note names the delta.** Two parameter limits may jointly falsify a premise
  neither falsifies alone, so a declaration above one parameter lists every theorem whose premises are jointly
  falsified but individually discharged. An empty delta is a claim, stated as one. A missing note is not an empty
  delta, and the declaration fails at the gate.

**Nobody ships the archetype.** The TLA+ properties are checked against an unshipped configuration. The article must say
so, with ISO 26262's safety element out of context (SEooC) as the precedent.

### 8.2 What the lattice has learned since

- **Axes named so far:** Persona provenance, event-log legibility, Observer scoping, effect-stream role, arguably
  HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability, and **floor verification** (ADR-0030). The set is not enumerated, and
  finiteness of each chain is unproven.
- **Two kinds of degeneracy, and type changes**, are now schema fields rather than observations (§8.1).
- **Composition** is owned by ADR-0023 and discharged through the composition note (§8.1).
- **Three obligations are deferred to a record of their own:** archetype versioning (conformance binds to an
  archetype version and a rung tuple, and published versions freeze), the dominance rule (the archetype moves on a
  paired axis only to Pareto-dominating values), and non-increasing TCB across archetype versions. They govern how
  the archetype *evolves*, which is a different subject from how a deployment varies from it.
- **The gap that leaves.** Clause 4 can force the archetype to grow whenever a variation fails admission, and until
  that record exists **nothing bounds how it grows.** This is named rather than papered over.

Declared records so far: **D-0024-1** (k-of-n grant seats) and **D-0024-2** (single signer) on approver fault
tolerance; **A-0025**, **D-0025-1**, and **D-0025-2** on anchor recoverability; **A-0030** and **D-0030-1** (a Rego
floor, tested rather than proven) on floor verification. D-0024-1 is now reachable: `quorum`
takes a threshold, and R9 keeps that threshold at two or more so the k-of-n rung cannot collapse into the
single-signer one. Fixing it was the archetype extension the admission test demanded, which is the test working as
designed.

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

**Where ratification stands (2026.09.25).** Twenty-nine records are Accepted (genesis); two remain Proposed, both
blocked on decisions rather than on missing text. The confirmation-required set is **nine**: ADR-0006 and ADR-0009
(C1, C4 via ADR-0013), ADR-0013 (C1, C4), ADR-0015 (C2), ADR-0023 (C3), ADR-0028 (C1), and since G2 ADR-0030 (C1),
ADR-0031 (C1), and ADR-0003 for its amendment A2 only (C1). One record is ratified in part: ADR-0022 §1–§5, §7 and
§8 are accepted, and **§6 is not**, because the confinement obligation it states is undelivered. The debt sits on
the face of that record. Accepted records now also carry **debts on their face** — ADR-0030's six, ADR-0031's five,
ADR-0033's Kafka row against ADR-0005 — which is ADR-0029 §2 working as written: ratification is available with
obligations open, provided the obligations are visible.

**Bootstrap trigger.** The anchor *may* bootstrap once a drafted TLA+ bootstrap specification exists: five modules
(`Genesis`, `Anchor`, `RulesFloor`, `Promotion`, `BreakGlass`), five invariants, and a mutation for each that must
fail. `RulesFloorNV` is a precursor, not a substitute. **Two of the five are drafted and checked** — `Anchor`
(`FloorPreserved`) and `BreakGlass` (`BreakGlassNeverChangesAuthority`). `Genesis` waits on the genesis rules
contents; `RulesFloor` and `Promotion` wait on modeling decisions about epochs, the vote triple, and veto seats.
`Promotion` also owes a model of deciding before committing, which the reference had to implement (§4.1).

**The trigger is permission, not obligation.** Meeting it starts nothing: bootstrap happens when the custodian
declares it **and** the trigger is met. A forcing function was considered and declined by name. Drafting the
remaining modules commits to nothing, and TLC checking is recommended rather than required — the ceremony accepts a
specification digest marked drafted-only.

**Ceremony.** Seat key-holders under a declared custody record. Assemble the **genesis bundle**: the corpus manifest,
including the confirmation-required set; the specification digest, marked checked or drafted-only; and the genesis
rules. Every key-holder signs its digest. That is issuance epoch 0. **The genesis bundle is the only artifact never
promoted.**

**After bootstrap,** each confirmation-required record goes through a confirmation promotion under ADR-0024 with author
recusal. Confirmed records lose the marker; rejected ones need a superseding record. Genesis records without the
marker are not re-reviewed.

**No forcing function.** Genesis may last indefinitely. In its place, every checkpoint carries a debt ledger (G1 §8).
The debt is visible, not bounded.

**Headcount.** ADR-0029 puts an archetype bootstrap at no fewer than five humans, and the derivation is now
recorded: three anchor key-holders (A-0025), two counted grant seats (R2), and disjointness between them (R5). If
the author holds a seat, recusal raises the roster to three and the figure to six. The four-human figure that
appeared in the 09.15 non-vacuity run is a property of that *model*, not a headcount — it declares custody (1, 0)
for the anchor, which is not archetype custody. **A solo bootstrap is not a bootstrap**, and custody today is
(1, 0).

**What the cleanup taught.** The freeze, recovery, fold, normalization, and G1 treated the corpus the way the pattern
treats artifacts: records identified by digest, changes recorded as typed history, and nothing applied that was not
ratified. Every pass found something the previous pass had missed, including this one. That is the practical form of
ADR-0029's weakest point: **the bootstrap set gets no independent review, ever**, so the only reviews it receives
are the author's passes before ratification.

**What the reference taught.** Building the admit path did to the records what the cleanup did to the corpus: it
found what reading had missed. Eleven findings, three of which only running code could produce, changed five
records inside two days (§15). The lesson is the same one at a different layer: **a record that nothing executes
is checked only by the person who wrote it.**

---

## 10. Boundaries and assumptions

The **boundary register** lists fourteen boundaries, each with its cadence, its instant, its interval of untruth, and
its behavior when unavailable.

- **B8, Persona evolution, is the most critical:** an uncontrolled outer cadence with no instant. Apple Private Cloud
  Compute is a shipped counterexample showing it can be controlled.
- **Break-glass grants have no TTL expiry**, which breaks the monotonicity claim. A TTL is drafted as rules-floor
  entry R8 (ADR-0026 A1) and pending; it needs a mechanism clause to mean anything, and trusted time to be sound.
- **`Contained` may have no members** while the sandbox gap stands.

**The clock model is stated** (ADR-0032), and it is small because of its first clause: **clocks buy liveness, never
safety.** Epoch fencing carries safety without reading a clock, so an expired lease its holder still believes in is
not a containment violation. From there:
- **Intervals are trusted by failure direction.** One whose failure subtracts authority — lease expiry, passive
  e-stop, a vote timeout — may use a local monotonic clock with a margin that errs early. One whose failure adds or
  preserves authority — a break-glass TTL, Persona expiry — needs trusted time from outside the principal.
- **No safety decision reads a clock a principal supplies.** A timestamp in a payload is content, not a fact.
- **The timing property is a budget, `W + L + D < T_irrev`**, declared per effect class. The three terms are of
  three kinds: `W` is guaranteed by the mechanism, `L` is an emergent property of the Observer and is unmeasured, and
  `D` is an organizational commitment. The ordering `W < L < D` that earlier revisions quoted is a description of
  magnitudes, not a safety property. Where no budget fits — an effect irreversible on emission — the answer is not a
  faster clock: **the effect must not be expressible in the alphabet at all.**

**The register's assessment,** in brief. Strong: the unavailability column, cadence as a first-class axis, the CALM
result, and reading the register by its holes. Weak: no per-boundary adversary, no owner column, fail-closed
uniformity presented as costless, SLSA re-derived without citation. Uncomfortable: Knight and Leveson's evidence that
independence is empirically weak, and no timing budget for what is effectively a real-time safety architecture —
which ADR-0032 has since given a form, `W + L + D < T_irrev`, with `L` still unmeasured.

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
feature list, with 48 features under eight principles and the corrected tally. Both are due for regeneration and
predate two checkpoints now.

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
- **The timing budget is only partly expressible** in standard TLA+, and ADR-0032 no longer asks it to be: `L` is
  measured, not proven.
- **The floor now has a non-vacuity gate; TLA+ invariants still do not.** Cedar decides "not always-allows" per
  action (§2.2). For TLA+ the gate is still a convention: every property ships with reachability witnesses that
  must be violated, as `RulesFloorNV`, `NonComposition`, `FloorComposition` and `Lease` all now do.
- **A model can be too coarse to see a finding.** `Lease.tla` modeled one global epoch, so it could not tell
  revoking one principal from revoking all — and the cost of that difference is finding 5. The fix was a witness
  that the distinction is reachable, which is the non-vacuity convention applied to the model's own vocabulary.
- **`Voting` sits under a message-level `Paxos` at the reference**, as the first bullet requires; the reference's
  simulation checks `Voting`'s invariants on every durable vote.

---

## 12. Where the argument is thin

The open list is G3. In narrative terms, the argument is weakest in nine places.

1. **The sandbox gap.** Effect exclusivity, ADR-0015's exhaustiveness, and ADR-0022 §6's confinement all rest on a
   mechanism nobody has specified. Until it exists, the strongest claim TOPAK makes is an assertion. §6 was
   deliberately left unratified for this reason, which records the debt but does not reduce it. **This is the single
   largest gap in the pattern**, and no record can close it — only a mechanism can.
2. **Correlated review failure.** Unanimity multiplies reviewers without making them independent. Floor fitness is
   the missing gate, and it is still unowned.
3. **Author-only ratification.** Twenty-nine records were ratified by one person, nine of the items on 2026.09.25
   within two days of drafting. Nine carry confirmation markers and will be reviewed after bootstrap; **the
   bootstrap set never will be**, by construction — confirmation runs under those records. The only reviews they
   receive are the author's own passes.
4. **Anchor capture.** The residual is real, numeric, and the first line of any residual-risk statement.
5. **The archetype is unshipped.** Every theorem is about a configuration no one deploys, which is honest only if
   the declaration records are actually written. None has been.
6. **The archetype can grow without a bound on how.** Clause 4's admission test forces extension; the record that
   would constrain the direction of that growth is deferred (§8.2).
7. **Checks are evidence, not attestation.** Nine TLA+ modules, the floor gates and a running reference now exist,
   and every mutation fails as it should. They were written and run by the same person who wrote the records, at
   small constants. TLC at these sizes is a discrimination test, not a proof, and **agreement among records, checks
   and code written by one hand is not independence** (ADR-0033).
8. **No floor is ratified.** The machinery that checks a floor is accepted; the genesis floor itself is a draft that
   passes the gates. Whether it is the *right* floor is floor fitness again (item 2).
9. **The replicas are trusted.** The mechanism's consensus replicas are crash-recovery, not Byzantine (ADR-0033 §3).
   Agents stay Byzantine at every position, but a compromised replica could propose an admit no floor ever
   evaluated, and the apply-time checks stop stale admits, not forged ones. Replica authentication and a Byzantine
   alternative are both open.

---

## 13. Assumptions of use

The boundary register's highest-leverage fix was to put assumptions of use at the front, framed as a safety element
out of context. This is that list. **A deployment that does not meet these does not inherit the theorems.**

| # | Assumption | If it does not hold |
|---|---|---|
| **A1** | **Effect exclusivity is enforced by a mechanism**, not asserted: no shell, no network egress, no filesystem outside workspace and corpus root, no path to the artifactory except `Submit` | `Contained` has no members; every containment theorem is void, and the enumeration in §4.1 is falsified rather than weakened |
| **A2** | **Every allowlisted tool is hermetic** — no network, no filesystem outside the workspace, deterministic given its inputs | One tool with a socket collapses the alphabet to a single variant and makes the envelope vacuous |
| **A3** | **The anchor's key-holders are honest at the declared capture threshold** | A coalition at that threshold issues any floor-conformant rules. No safety theorem covers anchor intent |
| **A4** | **Grant seats review independently**, against evidence not derived from the author's artifacts | Unanimous reviewers reading the same vacuous gate output fail together; the quorum multiplies signatures, not judgment |
| **A5** | **A trained, authorized human is present** for break-glass, quarantine release, and the detection interval `D` | The HITL and HOTL postures degrade to unattended operation, which the pattern does not model |
| **A6** | **Trusted time exists** for every interval whose failure preserves authority — a break-glass TTL, Persona expiry, re-attestation (ADR-0032 §2) | Those intervals can be stretched by a slow clock. Intervals that subtract authority need only local monotonic clocks, and no clock failure costs containment |
| **A7** | **The deployment declares its degeneracies**, with kind, type changes, and a composition note | The deployment's theorem inventory is unknown, and conformance claims are unfounded |
| **A8** | **Confirmation-required records are cited as author-ratified** until a first quorum confirms them | A publication overstates nine records, including both privileged-path records, the floor language, the lease, and the exhaustiveness claim |
| **A9** | **The mechanism's replicas are not compromised** — crash-recovery, authenticated to one another (ADR-0033 §3) | A Byzantine replica can propose admits no floor evaluated; the apply-time re-check does not re-run the floor |
| **A10** | **Each effect class declares `T_irrev`**, and `W + L + D < T_irrev` holds for it (ADR-0032 §4) | The HOTL posture has no budget; an effect irreversible on emission must be removed from the alphabet |

## 14. The step-6 findings, and where they went

Revision 5 carried eighteen findings from writing the narrative against G1. All are dispositioned as of 2026.09.23.

| Finding | Subject | Outcome |
|---|---|---|
| S6-1 | G1 cut but not uploaded | Uploaded; canonical bytes restored |
| S6-2 | k-of-n unreachable from the mechanism | **Mechanism extended.** `quorum` takes a threshold; R9 added to keep it above one |
| S6-3 | Recusal hard-coded, R3 vacuous | **R3 withdrawn.** Recusal is a mechanism constant in the `Vote` envelope |
| S6-4 | Genesis rules "checked at promotion" | Discharged by `GenesisSatisfiesFloor` at bootstrap |
| S6-5 | Non-erasable votes on erasable topics | Authoritative vote is the consensus-log admit decision; the topic carries a pointer |
| S6-6 | "The floor" ambiguous; rules-floor changes unlisted | Qualified to the policy floor; rules-floor changes added as a fifth rules item |
| S6-7 | "The anchor is at the gate" unqualified | Qualified to archetype custody; "(HITL)" kept |
| S6-8 | ADR-0024 depended on a separately queued record | Promotion made self-contained; ADR-0021 stays in its own queue |
| S6-9 | `Resign` undefined | Defined per custody rung in the ADR-0025 annex |
| S6-10 | Headcount four versus five | Five, with the derivation recorded; four is a property of the model |
| S6-11 | Crypto-shredding misstatement | Corrected in ADR-0021; erratum ratified on ADR-0020 |
| S6-12 | Break-glass missing from the authority set | Classified as an admit decision against its exception entry |
| S6-13 | "Every grant is a roster quorum" overreach | Scoped to privileged grants |
| S6-14 | Forensic horizon ends at re-genesis | Carried into the re-genesis migration obligation; open before confirmation |
| S6-15 | Veto seats cite reversed scoping | Carried into the ADR-0008 supersession's scope |
| S6-16 | Stale consequences in ADR-0010 and ADR-0012 | No amendment: the decision text stays true |
| S6-17 | Which rules are resident | Issued rules persist with genesis residency |
| S6-18 | Checkpoint file-name collision | Dated revision suffix; carried as convention in G2 |

Two findings changed mechanism text and forced the non-vacuity rerun (§7.3). One — S6-16 — was closed by deciding
that nothing needed to change, which is the amendment test doing its job.

---

## 15. The reference implementation

Until 2026.09.24 the corpus argued about a mechanism that did not exist. The TLA+ artifacts checked envelopes, the
floor was gated, and nothing composed them. ADR-0033 records what building one showed.

**What it is.** `mechanism/` implements the admit path end to end: epoch fence → lease → syntactic lift → floor →
bundle → consensus-ordered admit → effect, for Build's six actions and two provisional Run actions. Each letter is
filled by one instrument, by role:

| Letter | Instrument at the reference |
|---|---|
| **T** | TLA+ unchanged; its properties restated as Rust tests with the same mutations |
| **O** | Cedar, linked, with the gated floor compiled in by path and refused at startup unless its bytes match the gated digests; OPA sidecar with an in-process WASM fallback bound to the lease's revision |
| **P** | Sans-IO Multi-Paxos, `Voting` under message-level `Paxos`, driven by a deterministic simulation |
| **A** | The alphabet as MCP tools, and nothing else |
| **K** | Kafka, one topic per principal per round, emissions after commit, denials unordered |

**What it is not.** It is **evidence, not the verified object** (ADR-0033 §1) — the same kind of evidence as a TLA+
check, cited by a manifest digest and a commit, with the claim scoped to what its tests check. It has never been
promoted, no promotion pipeline exists to promote it, and nothing in it is in any TCB. It is not a deployment: every
lease it issues is rung 0, so every principal it serves is `Mediated`, and it fails assumption of use A1. **A running
program invites being mistaken for the mechanism**, and this paragraph exists because saying so once is not enough.

**What it showed.** The records compose, subject to what it does not show (below): every link of §4.1's audit chain
has running code. Making them run took twenty-two assumptions and seventeen gaps, each tagged in the code, which
turns "the mechanism will handle it" into a list. And it produced eleven findings about the records themselves.

| # | Finding | Where it went |
|---|---|---|
| 1 | A gate case did not test what it named | The generator, fixed |
| 2 | "Narrow the bundle" named an order between bundles that does not exist | ADR-0031: renewal keeps the bundle (§2.5) |
| 3 | Subtractions that change replicated state must be ordered though not authorized | ADR-0033 §4; ADR-0015 points to it (§4.1) |
| 4 | Re-genesis reused round-topic names — shown live against Kafka | ADR-0003 A1 (§4.3) |
| 5 | With one global epoch, one revocation ended every live round | ADR-0031: two revocation tools (§2.5) |
| 6 | A round-coterminous lease needed the round, which was not a field — nor was the role the floor keys on | ADR-0031: both are lease fields (§2.5) |
| 7 | Local expiry cannot free the one-live-lease slot without being ordered | ADR-0031 E1 (§2.5) |
| 8 | Decision and commit are separated in time, so the mechanism checks run twice | ADR-0033 §4 (§4.1); the `Promotion` module still owes a model |
| 9 | A retrying Paxos host that also re-queues on step-down doubles its backlog per term | **Open**: the drafted `Paxos` module should model proposer retry |
| 10 | Most floor denials carried no reason | ADR-0030: *no permit matched* (§3.1) |
| 11 | Denials never reached the round topic | ADR-0020 implemented; ADR-0003 A2 for after the seal (§4.1, §4.3) |

**Three needed code to find.** Finding 1 surfaced because the linked engine reported a reason the command-line gate
never compared; finding 4 because a live topic received two chains' records; finding 9 because a simulation ran
out of memory. Finding 11 is the other kind: it was found in review, and it was the clause ADR-0020 had predicted an
implementer would drop.

**What it does not show.** Confinement — the MCP front door makes the alphabet the whole protocol, not the whole
channel. Tool hermeticity: tools are pinned by binary and schema digest and run in a cleared environment, and their
behaviour is unchecked. The Observer, the archive, erasure, masking, Persona attestation and bootstrap: none is
built. Scale and long-running behaviour: there are no snapshots, and every admit waits for a consensus round. And
that the floor is the right floor.

**How it stays honest.** The reference pins the digest of every record and TLA+ module it follows, and a test fails
when one changes or when the code cites one that is not pinned (G3 §5). Every change to a record in this revision's
window was followed by a failing drift check, a review against the code, and a re-pin. That is the discipline in
miniature: the reference is not trusted to track the corpus; it is checked for it.

---

## Appendix C. Changes from revision 6

- **State of record repointed** from G2 to G3. Counts updated: twenty-nine records accepted, nine confirmation-
  required (§0, §9).
- **The letters name roles** (§1): the O is a verified floor evaluator plus a bundle engine, Cedar and OPA at the
  reference.
- **§3.1 rewritten for ADR-0030.** Refinement by composition replaces refinement decided at promotion; the floor on a
  verified evaluator, linked; schema S enforced per request; no transpiler; D-0030-1; the bundle revision binding;
  deny reasons; the genesis floor as a gated draft. §3.2 gains the computed classification and the incomparable row.
  **§2.4's SMT sentence retired.**
- **Recusal's authority path corrected** (§2.4): a policy-floor relaxation, per ADR-0022 A1, not a mechanism release.
- **New §2.5, the lease**, from ADR-0031: twelve fields, one live lease, the fence, monotone renewal with bundle, round
  and role fixed, two revocation tools, expiry ordered.
- **§4.1 extended**: decide, order, re-check (ADR-0033 §4); ordering is not authorization; denials recorded but not
  ordered (ADR-0020). §4.3 gains ADR-0003 A1 and A2. §4.2 records ADR-0005's debt from the reference.
- **The clock model** (§10) from ADR-0032: liveness not safety, intervals by failure direction, the `T_irrev` budget;
  `W < L < D` demoted from property to description (§5.2, §11.3).
- **§7.8** grows from five layers to eight: evidence, credential and time added.
- **§11.3** records that the floor now has a non-vacuity gate and TLA+ does not, and the too-coarse-model lesson.
- **§12** from seven weak places to nine: no ratified floor, and trusted replicas. **§13** rewrites A6 and adds A9
  (replicas) and A10 (the timing budget).
- **New §15**, the reference implementation and its eleven findings.
- **Appendices A and B retained.**
- **Erratum (2026.09.25, after the G3 cut).** Four register corrections — "proven"/"proved" to "checked"/"must
  hold" in §3.1, §3.3, §7.2 and §8.1 — per G3 §8 ("No theorem is proved") and the 09.25 critical review
  (CR-25). No decision content changed. Rev 7 is cited by digest in no manifest or accepted record; this
  erratum changes the file's digest.

---

## Appendix B. Changes from revision 5

- **State of record repointed** from G1 to G2.
- **Findings markers cleared.** Every ⟨S6-n⟩ marker revision 5 carried is resolved; §14 is the ledger.
- **Mechanism corrections** from the 2026.09.23 ratifications: threshold `quorum` and the withdrawal of `"any"`
  (§7.1, §7.3); recusal as a mechanism constant and R3's withdrawal (§2.4, §7.1, §7.3); R9 added as a conditional
  entry; R6 effective; the vote record placed in the consensus log (§4.4); promotion made independent of the Build
  effect-stream scheme (§7.1).
- **New narrative:** the R9 independence result and the too-small-model finding (§7.3); demand type 5 declined
  (§3.3); resignation per custody rung (§2.4); the declaration schema's `kind` and type-change fields, and the
  composition note (§8.1).
- **New sections:** §13 assumptions of use, framed as a safety element out of context; §14 the step-6 findings
  ledger.
- **§12 rewritten** from six weak places to seven, adding author-only ratification of the bootstrap set, the
  unbounded direction of archetype growth, and the limits of the checks themselves.
- **Appendix A retained** as the record of what changed at revision 5.

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
