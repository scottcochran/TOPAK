# TOPAK — Theory of Operation

**2026.10.02** · revision 12 · **narrative only** · cut from Genesis Checkpoint G8 · supersedes revision 11 as narrative

Revision 12 is revision 11 corrected against G8. Between the cuts the corpus's formal layer changed kind, and
nothing else did. **Thirteen of the fourteen TLA+ modules are proved** with the TLA+ Proof System: every invariant
each module states holds of every behaviour of the module, for every constant the module's named assumptions admit,
under the hypothesis that the mutations which break it are absent; 2,417 obligations. **The method is declared**
(ADR-0046, Batch 25, C2 and C4): TLC checks the mutations and witnesses at small constants, the prover proves the
invariants, *proved* and *checked* name the two, and MAP 2.3 closes. The prover is a trusted-base row, T-0045-31,
and the proof modules are frozen by digest. Writing the proofs found five errors in the binding table, each corrected
with TLC rows. **Nothing about the running reference changed**: a proof is of a module, and T-0045-28 stands.
Passages those changes made false are rewritten, with one sentence in §15 that revision 11 should have corrected and
did not; the narrative spine is revision 11's and no section is added. Appendix H lists every change.

---

## 0. How to read this

**This document explains how the design fits together. It is not the state of record.** Status, readiness,
digests, the ratification queue, the genesis debt ledger, and the open list are in **G8**.

The narrative describes what the records say. Status words appear only where status changes the meaning — a
reversal in effect, a claim still carrying a confirmation marker, or a section of a record that was deliberately
left unratified.

**What "ratified" means here, and what it does not.** Forty records are now Accepted (genesis), two of them
in part, and one is superseded. Twenty-two of the accepted carry a confirmation-required marker — three, ADR-0003,
ADR-0029 and ADR-0031's C2, for a single amendment only — which means they were ratified by one person and must pass
an independent confirmation promotion after bootstrap. **Until then, any claim resting on those twenty-two is
author-ratified, and this document says so at each point rather than once in a footnote.** Ratification by a sole
custodian is a declaration, not a review. Since 2026.09.30 a further qualification applies to four texts, all now
ratified: ADR-0044 (Batch 17), ADR-0045 (Batch 22), ADR-0030 A1 (Batch 24) and ADR-0046 (Batch 25) were **drafted by the assistant** at
the custodian's request, with every choice marked as the drafter's, and the custodian settled them by ratifying the
text; A1's one open choice, the proof format and the checker, was settled by the first run, and ADR-0046's
condition that the custodian regenerate its evidence was run by the drafter at the custodian's direction. That is one step further
from review than the records they draw on, and each says so on its face.

**Findings.** Revision 5 carried ⟨S6-n⟩ markers where records disagreed. All are dispositioned; §14 lists each with
its outcome. Markers that remain in this text point to findings from the 09.16 critical review and the 09.17
narrative log that are open, not to corpus contradictions.

---

## 1. The pattern

TOPAK is an architecture pattern for autonomous multi-agent collaboration that is safe by design. The letters
name its five components:
- **T**, TLA+ (Temporal Logic of Actions): the formal specification, model checking and proof;
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
the gate is outside them and must be carried as an assumption or a declaration. **A principal holds exactly one
seat** (ADR-0037 §1), and an agent is not one principal but a *cell* of them (§2.8).

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

**Confinement is carried in the lease** as a profile digest and an attestation rung (ADR-0031 §3, §2.5 below), and
since ADR-0034 the rungs mean something (§2.6). **Rung 0 is `Mediated`, always.** `Contained(p)` now has four
conjuncts (ADR-0034 §4): a live lease at rung 1 or above, granted on an Attested verdict at the deployment's declared
rung; a profile that meets P3–P5, so no launcher, Wasm tools only, inference inside; an in-house Persona on
ADR-0017's axis; and **ADR-0017's lineage-independence criterion in force**. The fourth is ADR-0035, which is
Proposed, so **`Contained` is still unreachable at every rung today**. What changed is the reason: at revision 7 no
rung had semantics; now the criterion is the only missing premise. The draft of ADR-0034 read independence as not a
conjunct, on the ground that it serves the Observer and not effect exclusivity; the custodian kept ADR-0031's
stricter reading, and the option is recorded.

**Weakest-link provenance** is now numbered (ADR-0035 §2): a lineage is only as strong as its weakest round, a round
outside the cage makes the whole record *declared*, and a `Mediated` principal in the chain yields attribution, not
a safety property.

### 2.4 Build's alphabet

Each domain has a typed alphabet of its own, and no name is shared between them (§2.9). ADR-0022 gives Build one:
**egress only**, six variants.

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
  Each allowlist entry carries a hermeticity obligation. For tools packaged as Wasm components it is discharged by
  construction, ADR-0034 P4: instantiated per call, handed a workspace directory capability and nothing else. For
  native tools it is still unowned, and using one is a declared degeneracy (D-0034-3).
- **Alphabets are bounded by seat kind** (ADR-0037 §4; ADR-0043 §2 for Run). Only a `thinker` seat is ever issued
  `Draft`, `Invoke`, `Submit` or `Actuate`; an `observer` seat reads, emits and, on the veto roster, denies; a `grant` seat reads,
  emits and votes. The bound is floor text — forbid **B10**, and **B6** tightened so a roster seat of the wrong kind
  cannot vote — checked by the grant path first and the floor second, as recusal is. A Reader with `Draft`
  authority, the failure ADR-0022 named, cannot arise, because the Reader is not a principal (§2.8).
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

**Confinement is an obligation, and it now has a design** (ADR-0022 §6; ADR-0034): no shell, no network egress, no
filesystem outside workspace and corpus, no path to the artifactory except `Submit`. ADR-0034 discharges §6 for
Build as a specification: seven profile clauses, three attestation rungs and an appraisal at grant (§2.6). It does
not discharge it as a mechanism. The reference issues every lease at rung 0, the first launcher is a Proposed record
(§2.7), and until a guest runs under an attested profile **Build principals are `Mediated`** and every Build
containment theorem is conditional. The *sandbox gap* is now two halves: the design half is closed, the mechanism
half is not, and `Contained` may still have no members at all.

**Capability cost.** This is not how agents write code today: no shell, no package installation, no network, no
git. The article has to say so before a reader who has used a coding harness says it for us.

**The alphabet is the agent's interface at the reference.** The six variants are exposed as MCP tools and nothing
else, on a front door the mechanism owns (ADR-0033 §2). That makes the alphabet the whole *protocol*. It does not
make it the whole *channel*: an agent process with a shell never has to ask. The reference is the plainest
illustration of the sandbox gap there is, and ADR-0036 is the design that makes the channel and the protocol the
same pipe (§2.7).

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
- **Renewal only narrows.** It may narrow the alphabet or shorten the TTL. It keeps the bundle, the round, the role
  and, since A1, the confinement digest and rung: a change of any of them is a grant. Revision 7 let a renewal lower
  the rung; that was a silent downgrade, the failure ADR-0034 exists to refuse at grant, reachable through the
  renewal path instead, and the two records never met in a check until `Confinement.tla` modeled renewal (§2.6). A
  renewal now re-attests, and if the evidence no longer reaches the rung the lease lapses. Keeping the bundle means
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
  grant and assumed for the round; epoch, fence and rules epoch are compared on every action. It is the one slice
  of the trusted base that is derived rather than declared; the rest is ADR-0045's table (§7.9).
- **The TTL is bounded** (ADR-0031 A2, Batch 17): a lease's `ttl`, at grant and at every renewal, is at most
  `T_persona`, a policy-floor value, so the Persona is re-attested at least that often. It is a bound on the declared
  value; expiry still runs on the local clock, and ADR-0045 finding 2 says what that leaves (§10).
- **`principal` and `seat` determine each other** since ADR-0037 §1: one seat per principal, fixed at declaration,
  so "one live lease per principal" and "one live lease per seat" are the same rule. The reference had enforced only
  the second, and its test passed only because the helper derived the principal from the seat; `Seats.tla`'s
  `M_SEAT` is that behaviour, and the grant path now refuses it.

**Author-ratified.** ADR-0031 is confirmation-required under C1, for the break-glass lapse on revocation, and under
C2 for A1 only.

### 2.6 Confinement is attested at grant

ADR-0031 gave confinement a field and left the rungs undefined. ADR-0034, ratified 2026.09.28, defines them, and the
whole of it turns on one test the corpus already had: **delegate by failure direction.** The substrate may carry a
mechanism whose failure only subtracts authority; a mechanism whose failure could add or preserve authority is
authored by TOPAK and consensus-backed. Applied to the host: at rung 1 a faulty launcher produces a valid-looking
lease for a guest it did not confine, at rung 2 the hypervisor can alter a running guest after its launch
measurement, and only at rung 3 is every residual host power subtractive. **The archetype is rung 3**, a confidential
VM with an independent verifier; rungs 2 and 1 are declared degeneracies, and rung 0 is `Mediated` always.

| Rung | Evidence | Appraised by | An untrusted host can |
|---|---|---|---|
| **3** | Confidential-VM hardware report over firmware, kernel, root, profile and Persona digests | An independent verifier, a trust root of its own | Only subtract |
| 2 | Measured-boot quote over the same values | The mechanism, against the profile's reference values | Launch a rogue image (detected: *Contested*); alter a running guest (not detected) |
| 1 | The launcher's assertion | Nobody; the launcher is the attester by construction | Nothing, by assumption |

- **A confinement profile is a promoted Build artifact** fixing seven clauses: one channel and no network device
  (P1); a measured read-only root, the workspace and the pinned corpus root and nothing else (P2); no shell, package
  manager or interpreter reachable from the principal (P3); tools as Wasm components, per call, with a workspace
  capability only (P4); the Persona's weights inside the guest and in the launch measurement (P5); one principal per
  guest and one guest per round (P6); and its own reference values (P7). Build's profile is fully determined by the
  alphabet. Run's is unwritten still, and has a shape now: ADR-0042 §6, the one section of the Run records left
  Proposed, says P4 cannot hold for a Run tool and channel fidelity must replace it (§2.9).
- **Appraisal is a condition of the grant**, not a protocol of its own. The nonce is a hash of epoch, log index,
  principal and round, so freshness comes from the log and not a clock. One replica appraises and the verdict is
  ordered; at apply, each replica checks the verifier's signature and that the nonce's epoch is current.
- **Three verdicts.** *Attested*: grant at the declared rung. *Unattestable*: refuse, and never grant lower. *Contested*,
  signature valid and measurements diverging: refuse, and revoke the principal, not the profile, because one hostile
  host must not be able to deny every principal that shares a profile.
- **No silent downgrade, at grant and at renewal.** A principal whose evidence does not reach the declared rung is
  refused rather than granted as `Mediated`; downgrading would turn a declared vacuity back into a silent one.
  Renewal re-attests with a fresh nonce and keeps the rung (ADR-0031 A1). What re-attestation adds is freshness
  against the log and against reference values withdrawn since the grant; it measures the launch again, not the
  running guest, so it never turns *Contested*. Integrity of a running guest rests on the hardware at rung 3 and on
  the trusted base below it, never on re-attestation.
- **The session is the attested guest's.** At rungs 2 and 3 the attested session key replaces the reference's bearer
  token for principals. At rung 1 the launcher binds the session and is trusted to (§2.7).
- **This is PC/EC.** An unreachable verifier stops grants; live leases run to renewal; every refusal, expiry and
  revocation takes the path that needs no quorum.
- **The trusted base per rung is named.** Rung 3 adds the CPU vendor's root of trust and firmware, the verifier and
  the promoted image; rung 2 adds host firmware and the hypervisor; rung 1 adds the host operator and orchestrator.
  Rung 3 trades an assumption for a mechanism: A1 becomes a claim resting on named, audited components with a
  published attack history, which is still strictly more than A1 conditioned on nothing. ADR-0045 (Batch 22)
  flattens the per-rung table to one row per component with a rung range, T-0045-16 to T-0045-22, each with its
  residual on the face, and loses nothing in the flattening (§7.9).

**Checked.** `Confinement.tla` runs the host, the mechanism and two principals at each declared rung: `Safe` holds
at every rung; one mutation, the host untrusted where the rung trusts it, breaks containment at rungs 1 and 2 and
changes nothing at rung 3, which is the rung ladder checked rather than asserted; the renewal-lowers-the-rung
mutation breaks no-silent-downgrade at rung 3, which is the case A1 closed. **Rung 0 is now in the run too**
(ADR-0034 A1, Batch 17): the deployment D-0034-4 declares produces no `Contained` effect, checked rather than
declared, and cannot produce *Contested*, as at rung 1. The run also found that the module reads a launch
measurement at rung 0 under the host mutation, which rung 0 has no more than rung 1 does; the correction waits for
a successor module, since the digest is cited.

**Author-ratified.** ADR-0034 is confirmation-required under C2 and C4, and was drafted, revised twice and ratified by
its author within three days. **Almost nobody can afford the archetype**, as with ADR-0017: it needs confidential
VMs, confidential-compute accelerators, an in-house Persona and an independent verifier, and the record specifies the
rungs below it as carefully for that reason.

### 2.7 At rung 1 the launcher is the channel

The reference's front door is `topak mcp`, a stdio MCP server the agent runs, proxying to the node's agent socket
with a bearer token. A guest that speaks it needs the socket, and on the reference's host a Unix socket cannot be
shared into a container. So the guest has one channel, stdio, and something on the host must join it to the socket.
ADR-0036 (Proposed) makes that something the launcher, and the constraint turns out to be the corpus's own rung-1
shape: **launch, appraise, grant, bridge.** The launcher starts the guest with the profile's constraints and holds
its stdio; the guest verifies its Persona bundle and reports its identity; the launcher compares that and the image
digest with the profile's reference values, and only on a match asks for a grant at `[profile digest, 1]`; then it
attaches the token to every action line the guest writes and forwards it. **The token never enters the guest.** The
session is the pipe, the pipe belongs to one launched instance, and no other process can use the lease.

- **A profile declares what it fails.** The profile is a file whose digest is the lease's confinement digest, and it
  states P1–P7 as pass, fail or vacuous, with a reason and, for each fail, the subtraction that would fix it. A grant
  at rung 1 on a profile with a declared failure is valid: the rung says how the belief was established, the profile
  says what the guest is, and `Mediated` follows from ADR-0034 §4 as a computed verdict. That is what separates it
  from a rung-0 grant that names no profile, whose verdict is computed from nothing.
- **A rung-0 grant may name a profile too** (ADR-0036 R1). Then its verdict is derived from declared clauses, and the
  word beside each clause is *declared by the operator and verified by nobody*: rung 1 asserts, rung 0 declares. The
  trusted base at rung 0 stays empty, because nothing relies on the declaration, and a results file must print
  `[digest, 0]` and *declared* so nobody takes it for attestation. The reference's first declared profile is the
  host-run occupant's, `serve.py` on the host with no container, failing P1, P2 and P3 and passing P5. **The profile
  is the constant and the rung the variable**: the same schema is declared at rung 0, asserted at rung 1, measured at
  rung 2 and attested at rung 3, elevation is a fresh grant naming the same digest, and each step changes one thing,
  a clause verdict or the rung, never both. The rung-DAG analysis works that ladder as a path through its lattice.
- **The first profile, for the SLM inference image** (`slm/serve/`), passes P1, P2, P5, P6 and P7, is vacuous on P4
  because the occupant never `Invoke`s, and **fails P3**: the image carries an interpreter and a shell. That one
  failure is the subtraction list to a `Contained`-shaped guest, and it is a build task.
- **The occupant is a scripted round with the Persona inside.** `Read`, `Draft` of model-generated text, `Submit`.
  It mounts no corpus root, so its ingress is exactly its admitted `Read`s, which is what ADR-0035's `consumed` set
  records (§16).
- **Every failure subtracts.** No attestation, no grant; a dead guest closes the pipe and the round ends; a dead
  launcher takes the token with it and the lease expires.
- **The second step moves the launcher into the node**, as a `launch` operator request with a promoted profile. That
  is a mechanism change and gets its own addendum. Rung 2 is not on this path: a container has no launch
  measurement.

Nothing in §2.7 is ratified, and no rung-1 lease has been issued.

### 2.8 Principals, seats and cells

The corpus had said "principals are agent LTROs" since its first checkpoint, and the accepted text said something
else in three places: a principal holds one live lease and each lease names one seat (ADR-0031); the Observer can be
revoked on its own, which makes it a principal by the evictability test; and the draft floor's principal type is
`Seat`. ADR-0037 (ratified 2026.09.29, C3 and C4) follows the accepted text.

- **A principal holds exactly one seat**, fixed when the seat is declared, and **an LTRO is a cell**: the principals
  seated around one Thinker for a round. A cell holds no lease, speaks no alphabet and cannot be evicted as a unit;
  it names a binding, as a round does. Separation of duties inside an agent is therefore separation between
  principals, the only kind the corpus has machinery for.
- **Two positions are seats and two are stages.** The **Thinker** and the **Observer** are seats: each holds a
  Persona, a lease, a topic. The **Listener** is the environment step that delivers the task and the admitted
  `Read`s, with no Persona and no choice; at the reference it is the node side of `Read`, so ingress to the Thinker is
  exactly what ADR-0035's `consumed` set records. The **Reader** is a check, not a seat: its two admissible uses
  (ADR-0019) are decidable, and the interpretation ADR-0018 had given it is not kept, since a semantic reading made
  inside the watched fault domain by the watched lineage is the finding worth least. Each cell therefore has two
  cognitive seats, and ADR-0017's two lineages cover them; the "three seats, two lineages" finding closes without a
  third lineage.
- **Who forms the emission.** The Thinker's Persona, weights and decoder together, forms it; the mechanism's
  validator admits it; the Reader was never in that chain. What coupling the decoder to the Thinker gives up is the
  record's ability to say the model and its translator disagreed. A decoder seat would recover that at the cost of a
  third Persona per cell and is not taken. Instead **raw emission is retained at the archetype**, in the round topic
  beside the typed action, as cognitive payload under the same ACL and erasure unit, for one purpose: re-run the
  decoder and compare. It recovers faithfulness, not intent, and a deployment that does not retain declares
  D-0037-2.
- **Where the Reader runs, and what its facts are for.** It needs the logits, so it runs beside the Thinker, inside
  the guest at rung 1 or above, and everything it produces is the guest's own report. Its results cross into the
  control plane as facts and are consumed by the cell Observer, which issues any finding under its own lease. That is
  harmless for a deny and unsound for an admit, so **decoding conformance may admit only at a rung that attests the
  inference itself**, which none does yet; at rung 1 it may only deny. Logprobs are monitored and not retained.
- **Seat distinctness covers one pair per cell**, (`thinker`, `observer`), enforced where refusal stalls (ADR-0035
  §5). Two `thinker` seats on one Persona are two principals in two cells, and this is permitted; the correlation it
  creates is the correlator's concern (§5.1).
- **A human holds one seat too**: a `grant` seat, or a `thinker` seat as an author, never both at once. A person who
  authors and approves is two principals, and recusal is per seat and does not see through them, which is the
  seat-registration record's problem (G5 item 41). The old contrast, "human principals are atomic," stops being a
  contrast: every principal is atomic. What the LTRO gives an agent by default is an Observer in its cell; what a
  human lacks is effect exclusivity, which the LTRO never supplied.

**Checked.** `Seats.tla`: only thinker seats author and thinker seats never vote; no principal holds two live leases;
each mutation breaks exactly its property. The floor: 47 cases, B10 total and discriminating on all four authoring
actions. The reference: the grant path refuses both, and the author's voter grant is refused at the grant rather
than at the vote.

**Author-ratified.** ADR-0037 is confirmation-required under C3, for reversing three bullets of ADR-0018's Reader
scope correction, and C4. It was drafted, revised five times under the custodian's questions, run and ratified on two
consecutive days.

---

### 2.9 Run's alphabet

Until 2026.09.29 no record defined Run's alphabet: two provisional names, `RunInvoke` and `RunEmit`, had carried
ADR-0015's two effect classes in the floor and the reference since the reference was built, and ADR-0022 §5 said
`Read` and `Emit` were common to both domains while the floor scoped both to Build. ADR-0040, ratified 2026.09.30
(Batch 20, C3 and C4), gives Run **three variants and nothing shared but the carrier**:

| Variant | Class | Envelope |
|---|---|---|
| `Consult(ref)` | **Ingress**, no effect | `ref` resolves inside the pinned **Run root**, a second content-addressed set |
| `Actuate(tool, inputs)` | Effect: tool invocation | The tool is allowlisted by name and digest, and its entry **declares the channel it opens** |
| `Report(record)` | Effect: emission | The principal's own round topic, this epoch and round, unsealed |

- **A read of live state is an `Actuate`.** Anything not content-addressed in advance is reached through a tool,
  however read-only, because the request itself leaves the membrane. That one line is what the coupling exemption
  rests on.
- **No variant name is common to Build and Run** (ADR-0022 A2, C3, applied). A name in both alphabets would have to
  carry the same obligations in both, and `Invoke` is hermetic where `Actuate` exists to have an effect.
- **There is no terminal variant.** Run offers nothing to a gate; **a Run round ends when its lease ends**, and a Run
  seat cannot abstain (ADR-0042 §5).
- **The alphabet is minimal because its constraints live elsewhere**, each with an owner. **Policy** (ADR-0041, C1 and
  C4): one envelope per variant, `R4-consult-pinned` new; the coupling restated over effects and **not** extended to
  `Consult`; break-glass reaches `Actuate` and nothing else; argument constraints in the bundle tier, where they can
  only subtract. **Mechanism** (ADR-0042 §1–§5, C4): the sequence an Observer's watermark is over counts
  effect-bearing admits, so an invocation advances it as a report does (§5.4); **every admitted `Actuate` leaves a
  record on the round topic**, written by the mechanism when the call returns, its envelope as facts and its bodies
  as payload, and a call that returns after the seal delivers nothing; a tool's result is recorded ingress, which
  makes Run's ingress a closed list. **Cell** (ADR-0043, C4): the Listener delivers the task, each admitted
  `Consult`'s content and each admitted `Actuate`'s result, and nothing else reaches the Thinker; a `thinker` seat
  holds all three variants, an `observer` seat `Consult` and `Report`; the Observer's mark is over the effect
  sequence, so it reads results as well as calls, which is the first second reader on Run's ingress; and an
  Observer's lease must outlast its Thinker's to reach the seal.
- **What is left Proposed is confinement.** ADR-0042 §6 states Run's confinement obligation and does not deliver it:
  the effect channels are the tools', not the principal's, so **P4 cannot hold for a Run tool**, and channel fidelity,
  a tool opening the channel its entry declares and no other, replaces it. Nothing checks it (`mechanism/` G19), the
  Run profile that would carry it is unwritten, and the custodian left §6 out of the batch, as ADR-0022 §6 was left
  out at B2. Every Run containment theorem is conditional on it.

**Checked.** `RunCoupling.tla` separates the counters `Coupling.tla` had merged, and its mutation `M_EMITSEQ`, the
sequence counting reports only, is the reference's behaviour before 2026.09.29: a Thinker that never reported could
invoke up to the round bound with its Observer's mark standing still. `RunSeats.tla` holds `Actuate` to `thinker`
seats and no name across domains. The floor was gated with the three actions and two new controls, and the
reference exposes three Run tools and nothing else (ADR-0033 A3). The reference's own build of ADR-0041 found that
its §7 named the wrong gate for one control; the record was revised before ratification.

**Author-ratified, and more.** All four records carry confirmation markers; ADR-0040 and ADR-0022 A2 carry C3. They
were drafted on 09.29, built the same day, and ratified the next, with the custodian settling eleven choices in
discussion and the rest by ratifying the text.

---

## 3. Policy

### 3.1 The verified object and the policy floor

Moon & Varshney put boundary policy inside the verified artifact. TOPAK externalizes it into signed bundles that
change at runtime, and bounds them (ADR-0010).

**The verified object** is the enforcement mechanism, its version pinning, its epoch fencing, a **minimal policy
floor**, and (per ADR-0010 A1) a **minimal rules floor** (§7.3). Operational bundles are versioned parameters. They
may subtract authority, never add it. **And a bundle is trusted by its signature, not its file name** (ADR-0044,
Batch 17, C1): the signing key is carried in the issued rules, the signature covers the content revision, the
mechanism loads a bundle only when it verifies, and signing happens at promotion. The record is in force and the
reference implements it since ADR-0033 A6 (Batch 23): a bundle loads only under a signature that verifies against
the rules' keys, today a dev key with custody (1, 0), and signing at promotion is a script step because no promotion
pipeline exists (§15).

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

**One step at the gate was trusted, and is now checked.** The routing of a floor change (§3.2) rests on two
"implies" answers, and an "implies" that holds is an UNSAT result from the solver. The encoding is sound by proof;
the solver is not, and a wrong `holds` classes a relaxation as a tightening, which then passes by promotion alone.
ADR-0045's admission rule (§7.9) refuses that: the solver's failure adds authority and no issuance fixes a solver's
honesty. **ADR-0030 A1 (Batch 24)** keeps the routing table and moves the trust: a `holds` verdict counts only with
the query it answered, the proof the solver produced and a pinned, independent checker's acceptance, their digests
in the gate evidence; a `refuted` verdict needs none, since it can only subtract. The gate run invokes the solver
through a wrapper that keeps the query, prefixes the proof with declarations derived from the query's own text,
requires every assumption the proof makes to be one of the query's assertions, and forwards `unsat` only after the
checker accepts; the checker is `ethos` at a pinned commit, checking cvc5's proofs against cvc5's own rule
signature, which is tracked and measured, so the trust has moved from a solver's search to a rule set read as
written. What the checker does not reach is said: cedar decides most of the totality gate by folding the authorizer
term without any query, and those verdicts rest on the engine's faithfulness (T-0045-3), not on a proof. A
deployment that runs the gates without the checker declares **D-0030-2**, routing verdicts unchecked, whose
subtractive mitigation is to make every floor change two-key; every gate run before 2026.10.01 was one.

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

**The genesis floor exists, as a draft.** Seventeen Cedar policies, schema S and, since ADR-0039, a **values file**,
gated six times, last on 2026.10.01 with proofs behind it: every policy never errors on every action it covers,
every action of the nine is neither always-allowed nor always-denied, removing any one policy changes the floor,
four deliberately broken floors were caught, two of them for `Consult`, and three lying solvers produced a failure
and never a `holds`. The values file holds the numbers the typed lift reads that
Cedar text cannot, `K`, `T_obs`, `T_persona` and the unset θ, and its digest is pinned with the floor's and the
schema's; every number in it is a placeholder and says so. The text is **not ratified**; ADR-0030 ratified the
language and the machinery, not a floor, and ADR-0041 ratified what a Run floor must contain, not this one.

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
into the gate evidence that votes already bind to. **What a Byzantine author cannot do, a wrong solver could**, until
ADR-0030 A1 (Batch 24): a `holds` now counts only with a proof the pinned checker accepted, and the solver is trusted
for nothing (§3.1).

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
  the orderable event. In Run the variants are `Actuate` and `Report`; `Consult` is ingress and no effect (§2.9).
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

This makes **effect exclusivity a mechanism claim** — TOPAK's sharpest differentiation from Moon & Varshney's
assumed version once the confinement obligation (ADR-0022 §6) is discharged, and identical to it in strength
until then (ADR-0015 E2). The design of the discharge now exists (§2.6) and the mechanism does not (§2.7), so the
two positions are still identical in strength. Any sideways effect path falsifies the enumeration rather than
degrading it.

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
(ADR-0003). Since A3 (Batch 17) the last clause is scoped: one store for a topic's whole retention, never a
retention length, which is per use and per domain, and the archive is not a tier. The **topic is the unit of
erasure**. Deleting a sealed container never edits a signature or a hash
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

**Scoping, decided.** ADR-0008 was accepted with a shared, orchestrator-level Observer group; ADR-0023 found that
neither that nor per-principal Observers dominates, and owed a superseding record. **ADR-0038 (ratified 2026.09.29,
C3 and C4) is that record, and ADR-0008 is superseded.** The archetype is **one `observer` seat per cell plus a
correlator**: the cell Observer watches its Thinker and reads its round topic in full; the correlator is ADR-0008's
shared group under a new name and a narrower job, watching every cell in its domain for what no single cell can see,
and carrying none of any cell's own detection. A compromised cell Observer costs one cell's detection; a compromised
correlator costs cross-cell detection only.

- **The watched-by relation is the ACL.** `W(p)` is the set of `observer` seats whose lease holds a read
  authorization on `p`'s round topic: its cell Observer and the domain's correlators. It is a fact in the mechanism's
  state, and it is the relation coupling (§5.4) is written against, so either record can be superseded alone.
- **What the correlator reads.** At the archetype, everything the shared group could: every cell's admits and
  denials with their sequence numbers, cell Observers' findings and the Reader's facts as control-plane records, the
  typed envelopes, and the payloads under the ACL. A facts-only correlator is a permitted narrowing, declared as the
  mitigation on D-0038-2, that gives up cross-cell semantic detection for immunity to injected content. Its detection
  *function* is still unspecified (G5 item 43); what it reads is not.
- **Placement**, ADR-0008's rule carried forward for seats: no `observer` seat shares a device with a Thinker it
  watches, and no two members of `W(p)` share a device. The reason no longer rests on a quorum. It is correlated
  failure and an effect path through device memory, and both hold whether or not anyone votes. The Reader stage may
  still colocate.
- **Observers combine by any-of, and there is no Observer quorum.** Every Observer output is a denial or a trigger for
  one, so a finding from any member of `W(p)` takes effect and no agreement is sought. ADR-0008's replicas become
  additional seats. More Observers never lower safety and may lower availability, which is the monotone direction; a
  quorum, by contrast, would let a compromised majority suppress an honest finding, and `Observers.tla`'s `M_QUORUM`
  shows exactly that trace.
- **The veto roster holds cell Observers and correlators** (ADR-0038 §6, applied to ADR-0024 by A2 during genesis,
  which is what avoided reaching a bootstrap record through a post-bootstrap promotion). A veto seat's alphabet is
  unchanged: `Vote(deny)` only.

**Monoculture.** An Observer should come from a different model family than the agents it watches. Sharing a family
is a shared blind spot. Since ADR-0037 the predicate has one pair per cell to cover.

**Author-ratified.** ADR-0038 is confirmation-required under C3, for the supersession, and C4. Its correlator reads
every cell's payloads at the archetype, so it is the one place an injection in any cell can arrive; the bound is on
what a compromised correlator costs, not on whether it can be compromised.

### 5.2 Build has an Observer

A hostile domain with enforcement and no detection was the sharpest contradiction on the board. ADR-0021 closes it
by reusing Run's round-topic scheme:
- **A Build round is one pipeline invocation.** Each principal seat holds its own topic.
- **Sealing moves to submission.** The principal's topic set is sealed when the artifact is submitted.
- **Retention diverges by parameter.** Build topics live as long as any artifact promoted from them. The mechanism
  is the same.
- **Build's Observer follows ADR-0038 placement**: one per author's cell, more by any-of, cross-family, deny-only.
- **A promotion needs coverage** (ADR-0039 §3; ADR-0024 A2.3): the author's cell Observer must have reported reading
  the author's round to its seal, or the round stalls. Coverage is a fact, not a "no finding" attestation; whether the
  Observer objected is still only `Vote(deny)`, and its silence is still not a veto. A2.2 adds that the veto seat must
  be leased with a Persona independent of the author's, which the reference cannot yet check (`mechanism/` G18).

**Timing runs the right way.** Run's budget is hard: the propagation window `W` is about a second and no human fits
inside it, so Run is human-on-the-loop (HOTL). Build favors consistency over latency and its promotion
gate blocks, so Build detection only has to finish before the gate clears. Detection is cheaper in Build, which
makes its absence harder to defend. ADR-0021 was corrected for quorum promotion — every vote covers the artifact
digest and the sealed topic-set digest, and the grant seats authorize, not a human key — and held for eighteen days
on one clause: its long Build retention against ADR-0003's no-tiered-storage rule. ADR-0003 A3 scoped that rule to
the store rather than the length, and ADR-0021 was **ratified 2026.09.30 (Batch 18, C4)** after a read-through
for the ADR-0008 vocabulary ADR-0038 had retired. The reference already emits Build rounds to sealed topics and
seals at `Submit`, which is §1–§3 as written; it has no Build Observer beyond the e2e fixture, so §5 and §6 are in
force and not exercised.

### 5.3 What logprobs can and cannot do

Interpretability can make `L` measurable, but only statistically, which turns a hard bound into a confidence
bound. White-box Observers also raise model-family coupling, against the monoculture rule. ADR-0019's narrow form
(§6) guards against drifting there by accident. Since ADR-0037 the logprobs are consumed by the Reader *stage*, whose
two results are facts for the cell Observer, and the admitting use, decoding conformance, waits on a rung that
attests inference (§2.8).

### 5.4 Liveness is coupled to admission

Detection failed open: an Observer that was dead, partitioned, starved or colluding produced the same observable as
a clean system, and no record said whether that was accepted (the 09.16 review's CR-2). **ADR-0039 (ratified
2026.09.29, C4) couples, and declares the part coupling cannot reach.**

- **Liveness is progress, not presence.** An `observer` seat reports by emitting a **heartbeat**, a fixed-schema fact
  naming a watched round topic and a **watermark**, the sequence number through which it says it has read. The
  mechanism keeps `heard(o)`, when it last admitted one, on its own clock and per replica, as it keeps lease expiry;
  and `mark(o, round)`, replicated from the log, rising and never falling. `live(o)` holds when the lease is live,
  fewer than `T_obs` have elapsed since `heard(o)` with the asymmetric margin, and `seq − mark < K`: the strict form,
  so that after the admit being decided at most `K` emissions are unread. `≤ K` admits a `K+1` backlog, which the
  model found. **In Run the sequence counts effects, not emissions** (ADR-0039 A1, ADR-0042 §2, Batch 20): an
  `Actuate` advances it as a `Report` does, and `Consult` advances nothing. The record's bound had been written for a
  Run whose two variants were both effects; the reference had counted emissions only, so a Thinker that never
  reported could invoke up to the round bound unread, and its round sealed at zero.
- **Run: every effect-bearing admit under a Thinker needs a live cell Observer**, the floor entry **R3**, deny-only,
  scoped to `thinker` seats so that an Observer's own heartbeat is not refused by the rule it exists to satisfy, and
  not extended to `Consult` (ADR-0041 §2): a read of pinned content adds nothing to the backlog and can be
  reconstructed from its digest at any later time, and a principal with a lagging Observer can still read and
  cannot act, which is the direction that fails closed at the lower cost. A dead or slow
  Observer stops its own Thinker and nothing else; the Thinker waits and is not evicted. **Coverage carries across
  rounds at the grant**: a Thinker's next round is granted only once a cell Observer has read its last round to the
  seal. Without that, the sequence and the watermark both restart with each lease and the check passes at the start
  of every round, which is how the first draft read; the custodian's question "isn't `K` bounded by the round's
  lease?" found it, and the answer was: within a round, by `R`, and across rounds by nothing.
- **Build couples the gate, not each admit** (§5.2), because the gate blocks and detection only has to finish before
  it clears.
- **The correlator is never coupled.** Coupling to it would make one seat's liveness a precondition for every admit in
  its domain, the fleet-wide stall ADR-0038 exists to avoid. Its absence is visible, since it heartbeats too, and costs
  cross-cell detection only.
- **What this bounds.** `L` stays unmeasured. What coupling bounds is next to it: at any moment at most `K` of a
  Thinker's emissions are unread by an Observer that has reported in within `T_obs`, all of them in its current
  round. It is a count, not a time, and it holds only for an Observer whose watermark is honest.
- **What it does not cover.** Coupling closes three of CR-2's four cases and leaves **collusion** open: a colluding
  Observer heartbeats, reports a watermark and finds nothing, all its own assertions. Lineage independence is the
  cover the corpus has, the correlated-miss test measures it, and the residual-risk statement must say *detection
  fails open against a colluding Observer*.
- **The costs are stated.** The Observer is on Run's hot path for liveness, not judgment; a cell's availability is the
  product of its Thinker's and its Observer's; heartbeats are admits on the consensus log; and **R3 couples break-glass
  too**, so an emergency path waits on a dead Observer. That last was ratified as written and is the first thing a
  reviewer should reopen.
- **The numbers are placeholders.** `T_obs` 5000 ms, `K` 8, Run's `R` 64, chosen for order of magnitude so the runs had
  values; deployment or rung choices, declared per deployment, not the pattern's.

**Checked.** `Coupling.tla` over two rounds: no admit without a live Observer, the unread bound, and the correlator
never gating, each broken by exactly its mutation, and uncoupling breaks the bound as well as the property, which is
D-0039-1 as the record states it. `RunCoupling.tla` repeats it with three actions in place of one, and its
`M_EMITSEQ` is the reference before ADR-0042 (§2.9). The reference shows every refusal: no Observer lease, no heartbeat, a dishonest
heartbeat, a backlog of `K`, presence without progress, staleness after `T_obs`, a second round granted while the first
is unread; and one promotion stalled for coverage and completed by a heartbeat to the seal.

---

## 6. The model is pinned

Before the Persona series, everything in the system was pinned except the model. ADR-0016 to ADR-0020 close that
asymmetry.

- **The Persona** (0016) binds a model to its complete runtime configuration: provenance and cryptographic
  identity, system prompt, decoding parameters, decoder identity and hash, decode-observability class, and seat
  binding, whose values are now `thinker` and `observer` (ADR-0037). It is a verified artifact.
- **The archetype admits only in-house pre-trained Personas** from two independent lineages (0017). Overlapping
  public corpora do not count as independent. The admission clause stands; its ordering-primacy clause is reversed
  in effect by ADR-0023 (§8.3).
- **The typed lift splits** (0018). The model-specific decoder ships in the Persona; the model-agnostic validator
  lives in the mechanism. This is the ADR-0010 move (verified core, parameterized edge) applied to syntax. Its Reader
  scope correction is reversed in effect by ADR-0037 (§2.8): the Reader is a stage, not a cognitive seat. The split
  itself stands.
- **Decode observability is narrow** (0019). `none` is the only unconditional value. `topk_logprobs` is admissible
  for decoding conformance and substitution detection only, never for claims about `L`.
- **Replay scope is boundary events only** (0020), with explicit revisit triggers.

Havoc semantics still make a *worse* model harmless for containment. What changes is that silent substitution
becomes a detectable identity mismatch instead of an unmodeled event. None of these records adds a floor
exception: revocation, decoder failure, and subtraction are all denies. The Persona is a lease field (§2.5), so a
revoked Persona is a targeted revocation: its leases end, it is barred from later grants, and no other round stops.

**Lineage is a projection, not a claim** (ADR-0035, Proposed). ADR-0017 required two independent lineages and left the
criterion outstanding; the obvious criterion, compare two training manifests, checks what the author claims, and
Build is where the Byzantine threat lives. So the lineage record is computed by the gate from the consensus log: the
artifact DAG under the weights, with what each round could read (`ingress`, over-approximated) and what it did read
(`consumed`, never over-approximated), which models generated or curated its data, its tokenizer, architecture family
and trainer, and the lowest confinement rung in the DAG. An authored manifest is kept only as a cross-check, and a
divergence is *Contested*. Independence is an exclusion rule over two records, E1–E5: distinct weights, no common or
cross generator, corpus overlap under threshold, different architecture and tokenizer, no common curator, plus a
distillation rule. The thresholds are policy-floor values. **Every share the gate computes is an upper bound**:
numerators over what the rounds could have read, the denominator the smaller consumed set, so charging a round with
more corpus can only fail it. It is enforced where refusal stalls, at the promotion tally and the deployment
declaration, never at grant, because an empty veto seat vetoes nothing. §16 records what rehearsing it found.

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
  held by every cell Observer and every correlator in Build (ADR-0024 A2.1, from ADR-0038 §6) and can only deny. Under
  unanimity every seat is a veto; a veto seat is one whose alphabet lacks `grant`.
- **Veto-seat silence is not a veto.** Requiring an Observer "no finding" attestation would make semantic judgment an
  enabling condition, which ADR-0007 forbids. **But an absent Observer now stalls rather than vetoing nothing**
  (A2.2, A2.3): a promotion completes only if a veto seat independent of the author was leased for the round and
  the author's cell Observer reported coverage to the seal. Both are mechanism constants in the tally, as recusal
  is, and both add a liveness assumption about an Observer beside the one about people.
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
carry one — confirmation runs under this record, and confirming it under itself would be circular. A2 was ratified
in genesis for that reason too: after bootstrap it would have reached a bootstrap record through an ordinary
promotion. Its safety rests
on the genesis attestation and the intent axiom until bootstrap, when ADR-0029 A2's full-corpus review reaches
it — a reader, not a confirmation promotion, which it can never have (§9).

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
rosters, the anchor's own key set, any relaxation of the policy floor or new exception, **any change to the
rules floor in either direction**, and, since A1 (Batch 17), **the keys the mechanism accepts a signature from in
place of its own check**: the rung-3 verifier's appraisal key and the bundle-signing key. Each decides what the
mechanism will admit on the strength of a signature, so replacing one adds authority and is an issuance. Tightening
the *policy* floor is not a rules change — it is an ordinary promotion. The rules floor is the exception, because tightening it constrains the anchor itself, so the anchor must
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
| Credential | Renewal only narrows and keeps the rung; widening needs a fresh grant after the round ends | ADR-0031, A1 |
| Confinement | A principal below the declared rung is refused, never granted lower; every host failure the archetype tolerates subtracts | ADR-0034 |
| Lineage | The projection over-approximates what a round could read, and adding to it can only fail a pair | ADR-0035 (Proposed) |
| Time | An interval whose failure subtracts may use a local clock; one whose failure preserves authority needs trusted time | ADR-0032 |
| Seat | Only a thinker seat is issued a variant that writes, runs or offers; adding a seat to a cell never adds authority | ADR-0037 |
| Detection | Observers combine by any-of, and coupling only refuses: more Observers never lower safety, and an absent one stalls | ADR-0038, ADR-0039 |
| Bundle | A bundle loads only under an issued key's signature; a file name is evidence of nothing | ADR-0044 |
| Trusted base | A component enters only if its failure can only subtract, or its identity is issued; what can add and is fixed by nothing is refused | ADR-0045 |

**At the pattern level it inverts.** Tightening the archetype puts every conformant deployment into declaration
debt. Relaxing it voids published theorems. Both directions cost something.

### 7.9 The trusted base is declared, row by row

Six records owed the trusted base rows and no two shaped a row the same way: ADR-0034 per rung, ADR-0036 per
component at one rung, ADR-0030 a residual with no table, ADR-0037 a fact about where conformance sits, ADR-0042
and ADR-0043 the tool host. ADR-0023 §6b required every degeneracy declaration to say what enters or leaves the
trusted base, and the field pointed at nothing. **ADR-0045 (drafted 2026.09.30, ratified 2026.10.01 in Batch 22, C2
and C4)** writes the table and, first, the
rule for being in it. The rule is §7.8's principle stated once for the trusted base, in ADR-0015's terms: *adds
authority* means an admit the rules in force would refuse, a promotion the tally would stall, or an issuance the
rules floor would reject, and nothing else.

- **Three classes and a refusal.** A **delegated** row's failure can produce only subtractions, and needs no proof, no
  key and no quorum; commodity substrate may fill it. A **trust root**'s failure can add, and the corpus trusts it
  anyway because an issuance or a promotion fixes its identity and its own record admitted it; the verifier is the
  model, and the bundle key and the replicas are rows of this class. An **excluded** row is relied on and trusted
  for nothing, so that every theorem premised on it is computed void rather than silently assumed: a native tool, a
  Run tool's declared channel, the rung-0 host, and the gate runner's evidence until its key is issued. Anything
  whose failure can add and whose identity nothing fixes is **refused**: it is inside the verified object, checked
  and not trusted, or the design changes until it can only subtract.
- **Rows are premise nodes.** Each row's *trusted for* sentence is a premise in the theorem DAG the 09.27 analysis
  described; an undeclared row is false, so a deployment that has not declared a component sits below every theorem
  on it, and type changes are rows, so §6b's field becomes a list of ids. Removing a row is a tightening and adding
  one is a relaxation that needs its own record, which is ADR-0023's non-increasing-TCB rule made checkable.
- **The archetype's table has thirty-one rows** in five groups: the assumptions under the mechanism constants
  (replicas, the signature primitive, the Cedar engine's faithfulness to its model, the clock, the transport, the
  bundle engines, the archive, the key store, the key-holders, the genesis rules, the corpus and its custodian,
  break-glass approvers); the Build toolchain; **the verified object's evidence**; the confinement axis; tools and
  the cell. The reference's own declaration is a second annex, and it ends with the inventory that leaves the
  reference: every theorem premised on confinement, gate evidence, hermeticity or channel fidelity is void there,
  which is §15's prose made row by row.
- **What applying the rule changed.** Of the eight components the 09.28 prioritization proposed to delegate, two are
  trust roots, two delegated, two excluded, one not a row, and **one refused: the solver** (§3.1), whose row has
  since been rewritten for the proof checker that replaces it (Batch 24). Trusted time for
  R8 is refused too, which the prioritization already said. And the rule caught the record's own first draft:
  §5 had called the admit path, the tally and the log "checked, not trusted", which is true of the specification and
  false of any code that runs it. **What runs is a row**: the implementation as a refinement of the specification,
  the model checker at the constants run, the prover for the invariants it proves (T-0045-31, since Batch 25), and
  the build toolchain are trust roots for every deployment until a
  refinement chain exists, and the gap is a debt ADR-0033 owns, not a residual the archetype keeps (§15).

**Ratified, and already moving.** ADR-0045 was ratified in Batch 22 at its sixth revision, once the theorem-to-premise
binding table existed: `spec/theorem-premise-binding.md`, forty-two rows naming for every checked property the rows,
the degeneracy parameters and the declared gaps it rests on, with a last column that computes what holds at the
reference. Two Annex B rows have changed class since, each by a dependent entry on the owing record's ratification:
the bundle signer from excluded to a trust root under a dev key (Batch 23), and the solver's refused row to a trust
root for the proof checker, pinned by three digests in the gate header (Batch 24). A third dependent entry added a
row: **T-0045-31, the TLA+ Proof System**, a toolchain trust root beside TLC's, pinned by the binary digest every
proof results file prints (Batch 25, ADR-0046); TLC's row now bounds the mutations and witnesses only. The same
batch gave the binding table a proof column and five corrections that writing the proofs found: a theorem's
hypothesis is the set of mutations that break it, derived and checked apart from the table, and where the two
disagreed TLC sided with the proof. The binding table is a draft
revised with the records it binds; its versioning, with the table's, is still the archetype-evolution record's
(§8.2).

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

- **Axes named so far:** Persona provenance, event-log legibility, Observer scoping (now with its archetype fixed:
  per cell plus correlator, the shared group being D-0038-1), effect-stream role, arguably HITL/HOTL/HOOTL posture,
  approver fault tolerance, anchor recoverability, **floor verification** (ADR-0030), **confinement rung**
  (ADR-0034), **lineage strength** (ADR-0035), **Observer coupling** (ADR-0039), **emission retention**
  (ADR-0037), and now **the trusted base itself** as a coordinate beside theorems held (ADR-0045). The set
  is not enumerated, and finiteness of
  each chain is unproven. The 09.26 accounting found the word *rung* carrying four orderings, two of them numbered
  in opposite directions: provenance rungs ascend with weakness and confinement rungs with strength. Always qualify.
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
floor, tested rather than proven) on floor verification; **D-0034-1** to **D-0034-4** on confinement (rung 2, rung
1, a native tool, rung 0); **D-0037-1** and **D-0037-2** (no Observer in a cell; no raw emission retained);
**D-0038-1** and **D-0038-2** (the shared group only; no correlator); **D-0039-1** (Run uncoupled); **D-0042-1**
(effects counted and recorded as reports only, the reference before 09.29); **D-0044-1** (bundle signing off, the
reference before 10.01); **D-0045-1** (no trusted-base declaration at all: the bottom of every axis); **D-0030-2**
(routing verdicts unchecked: every gate run before 10.01, and any run without the checker); and, in Proposed
records, **D-0035-1** (a lineage that can only be declared) and **D-0036-1** (a profile with a reachable
interpreter). None of these is a deployment declaration; they are record-level entries, and the 09.26 accounting
notes that no record yet says how the two differ. **The five Observer and retention entries void no safety theorem**,
because the Observer is deny-only, and state their losses in prose: a detection claim, an audit, a bound on unread
emissions. ADR-0023 §6's schema has no field for that, and a *properties lost* field is proposed (G5 item 40). D-0024-1 is now reachable: `quorum`
takes a threshold, and R9 keeps that threshold at two or more so the k-of-n rung cannot collapse into the
single-signer one. Fixing it was the archetype extension the admission test demanded, which is the test working as
designed.

### 8.3 Reversals in effect

- **ADR-0008's shared Observer scoping** (§5.1). **Superseded by ADR-0038** on 2026.09.29; the colocation rule is
  carried forward.
- **ADR-0017's ordering-primacy clause.** Provenance as *the* deployment axis cannot survive per-axis rungs. The
  admission clause stands. The superseding record is still unwritten.
- **ADR-0018's Reader scope correction**, three bullets, reversed by ADR-0037 §3 (§2.8). The record is not
  superseded.

All three reversals happened during genesis by the author alone. That is why the superseding records carry C3 and
will need independent confirmation (§9).

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
  confirming them under themselves would be circular. The marker is all the circularity forecloses: since A2 the
  set is reviewed at bootstrap with everything else (below), before the rules it defines take effect.
- Until confirmed, a publication citing a confirmation-required guarantee says "author-ratified."

**Where ratification stands (2026.10.02).** Forty records are Accepted (genesis); one, ADR-0008, is
superseded; three are Proposed: ADR-0005, blocked on a decision; ADR-0035 and ADR-0036, blocked on evidence and on a
review. The confirmation-required set is **twenty-two**: ADR-0006 and ADR-0009 (C1, C4 via ADR-0013), ADR-0013 (C1,
C4), ADR-0015 (C2), ADR-0021 (C4), ADR-0023 (C3), ADR-0028 (C1), ADR-0030 (C1), ADR-0031 (C1, and C2 for A1 only),
ADR-0034 (C2, C4), ADR-0037 (C3, C4), ADR-0038 (C3, C4), ADR-0039 (C4), ADR-0040 (C3, C4), ADR-0041 (C1, C4),
ADR-0042 (C4), ADR-0043 (C4), ADR-0044 (C1), ADR-0045 (C2, C4), **ADR-0046 (C2, C4)**, and two records marked for one amendment only:
ADR-0003 A2 (C1) and ADR-0029 A2 (C3). Batches 17 to 21, all of 2026.09.30, ratified six amendments and ADR-0044
(17), ADR-0021 (18), ADR-0033 A4 (19), the four Run records with three amendments (20), and ADR-0033 A5 (21).
Batches 22 to 24, all of 2026.10.01, ratified ADR-0045 (22), ADR-0033 A6 (23) and ADR-0030 A1 (24); Batch 25, of
2026.10.02, ratified ADR-0046, with dependent entries in thirteen records. Two records are
ratified in part: ADR-0022 §1–§5, §7 and §8, with **§6 not**, since ADR-0034 discharges its obligation for Build and
not for Run; and ADR-0042 §1–§5, §7 and §8, with **§6 not**, Run's confinement obligation, left out by the custodian
as ADR-0022 §6 was. Accepted records carry **debts on their face** — ADR-0030's, ADR-0033's Kafka row and its
refinement chain, ADR-0034's, ADR-0045's — which is ADR-0029 §2 working as written; three debts that stood at
revision 10, ADR-0031's `ttl` check, ADR-0025's two schema fields and ADR-0044's implementation, were struck by
ADR-0033 A6. **One marking has no criterion:** ADR-0035 R2 is confirmation-required by custodian instruction, because
its measurement rule is a novel construction to be reviewed against practice; G4 carries it as a ledger line and asks
whether ADR-0029 needs a criterion for markings of that kind. **One kind of debt is new**: four texts were drafted
by the assistant at the custodian's request, ADR-0044, ADR-0045, ADR-0030 A1 and ADR-0046, each marking every choice
as the drafter's, and the custodian settled all four by ratifying the text. ADR-0029 has no criterion for that either,
and G8 carries it beside the ADR-0035 line.

**Bootstrap trigger.** The anchor *may* bootstrap once a drafted TLA+ bootstrap specification exists: five modules
(`Genesis`, `Anchor`, `RulesFloor`, `Promotion`, `BreakGlass`), five invariants, and a mutation for each that must
fail. `RulesFloorNV` is a precursor, not a substitute. **Two of the five are drafted, checked and, since
2026.10.02, proved** — `Anchor` (`FloorPreserved`, for every floor subset and epoch bound) and `BreakGlass`
(`BreakGlassNeverChangesAuthority`, with R7 in force); `GenesisSatisfiesFloor`'s shape is a lemma in both, proved of
the floor's definition and not of genesis contents, which are unwritten. `Genesis` waits on the genesis rules
contents; `RulesFloor` and `Promotion` wait on modeling decisions about epochs, the vote triple, and veto seats.
`Promotion` also owes a model of deciding before committing, which the reference had to implement (§4.1).

**The trigger has a second condition** (ADR-0029 A2, ratified 2026.09.25): an **independent review of the entire
corpus** — every record including the bootstrap set, the floors and schema, the specification set and its results,
the reference trees, and the derived documents, at one named manifest digest — by at least one reviewer who is not
the author, with every finding dispositioned: applied, declined with reasons, or carried as named debt. The
specification makes bootstrap possible; the review makes it permitted.

**The trigger is permission, not obligation.** Meeting it starts nothing: bootstrap happens when the custodian
declares it **and** the trigger is met. A forcing function was considered and declined by name. Drafting the
remaining modules commits to nothing, and TLC checking is recommended rather than required — the ceremony accepts a
specification digest marked drafted-only.

**Ceremony.** Seat key-holders under a declared custody record. Assemble the **genesis bundle**: the corpus manifest,
including the confirmation-required set; the specification digest, marked checked or drafted-only; the review
attestation — reviewers, manifest digest, scope, findings disposition (A2); the genesis rules; and, now that ADR-0045
is in force, the trusted-base declaration beside the custody record, since the five bootstrap modules rest on its
rung-0 rows and the ceremony's reviewers read them as such (§7.9). Every key-holder signs its digest. That is issuance epoch 0. **The genesis bundle is the only artifact never
promoted.**

**After bootstrap,** each confirmation-required record goes through a confirmation promotion under ADR-0024 with author
recusal. Confirmed records lose the marker; rejected ones need a superseding record. Genesis records without the
marker get no confirmation promotion; their review happened at the gate, under A2.

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
ratified. Every pass found something the previous pass had missed, including this one. That was the practical form of
ADR-0029's weakest point — **the bootstrap set gets no independent review, ever** — until A2 reversed it: the set
is reviewed at bootstrap with the rest of the corpus, and until that gate the author's passes remain the only
reviews it has had.

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
- **`Contained` has no members**, and will not until ADR-0035 is in force and a guest passes P3–P5 under an
  attested profile (§2.3, §2.6, §2.7).
- **Detection fails open against a colluding Observer**, and against nothing else that ADR-0039 can see (§5.4). The
  sentence belongs on the residual-risk statement, which is unwritten.

**The clock model is stated** (ADR-0032), and it is small because of its first clause: **clocks buy liveness, never
safety.** Epoch fencing carries safety without reading a clock, so an expired lease its holder still believes in is
not a containment violation. From there:
- **Intervals are trusted by failure direction.** One whose failure subtracts authority — lease expiry, passive
  e-stop, a vote timeout — may use a local monotonic clock with a margin that errs early. One whose failure adds or
  preserves authority — a break-glass TTL, Persona expiry — needs trusted time from outside the principal.
  **Persona expiry now has a bound and not a clock**: ADR-0031 A2 caps the lease's `ttl` at `T_persona`, which the
  mechanism can refuse at grant; expiry itself still runs on the local clock, so a clock slow beyond the margin
  extends the re-attestation interval past the bound. ADR-0045 finding 2 names it, and the honest reading is that A2
  bounds the declared value and the interval it bounds is `T_persona` plus drift, until a time source is a row.
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
6. **Their defining artifact, a machine-checked refinement from specification to running code, is absent here, and
   is now a named row** (ADR-0045 T-0045-28) and a debt with an owner. The first stage of a chain exists since
   2026.09.30: every behaviour the reference's tests exercise is replayed through an operational model of its state
   machine (§15). It is a mechanized link, not a refinement, and the guarantee delivered is still *Empirical* in the
   paper's own ordering. The proofs of the modules (ADR-0046) do not change this: they are of the specification,
   and they make the refinement's target precise and do nothing else for it.
7. **Their trusted list is shorter than ours and names the Dafny verifier**, which discharges every obligation
   through Z3 and emits no certificate. ADR-0045 §2 applied to the corpus's own gate refused cvc5 for exactly that
   reason, and ADR-0030 A1 put a proof checker behind it (§3.1), so a Dafny or Verus chain would not remove
   T-0045-28 here; it would replace it with a trust-root
   row for the verifier, which the paper accepts and this corpus would have to say. The chain shape the corpus has
   already accepted is ADR-0030 §3's: a Rust engine differentially tested against a Lean model whose theorems a
   small kernel checks. **The corpus now has a verifier in that position too.** The TLA+ Proof System proves the
   modules' invariants through Z3, Zenon and a temporal-logic backend and emits no certificate a kernel checks
   unless its Isabelle backend is asked to, which it has not been (G8, item 74). ADR-0046 made it a trust-root row,
   T-0045-31, which is what this item said the paper accepts and the corpus would have to say; the corpus has said it.

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
- **MAP 2.3 is closed** by ADR-0046 (Batch 25): TLC checks the mutations and witnesses, the prover proves the
  invariants, and the corpus says which claim rests on which.
- **Still gaps:** MAP 3.4 (operator proficiency), MEASURE 2.13 (floor fitness), MEASURE 3.2 (`L`, now with a mechanism-enforced count beside it), MANAGE 1.4 (residual-risk statement,
  headed by anchor capture and now carrying collusion), MANAGE 3.1 (monoculture, now a per-cell pair).

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
- **A model that omits a path cannot check a rule about it.** `Confinement.tla` checked no-silent-downgrade at grant
  and had no renewal step, so the renewal path that lowered the rung was invisible to it for three days. The fix was
  to model the path and add the mutation that uses it (`M_RENEWLOW`).
- **Evidence in a model must be what the record says is measured.** The first `Confinement.tla` read the running
  image as the measurement, which would have let re-attestation catch a guest altered after launch, and no rung's
  measurement does that. Corrected without changing a result, and the correction produced a finding of its own.
- **A property check can refute a record faster than a review.** ADR-0035 §2's monotonicity claim fell to a
  2,000-trial random check in the rehearsal on the day the record was written; the revision that leaned on the claim
  was written before anyone read the check (§16).
- **A bound can be true only in one of its two forms.** `seq − mark ≤ K` reads like the ADR's prose and admits a
  `K+1` backlog; TLC found it, and the record now says `< K` and why (§5.4).
- **TLC does not short-circuit a disjunction.** `round = 0 \/ mark[round] ≥ …` evaluates `mark[0]`; the guard has to
  be an `IF`. And an unbounded set of records as a variable is an unbounded state space; `Seats.tla` ran for ten
  minutes before its `acted` set was reduced to the pairs the properties read.
- **Three tests failing on one line is a rule refusing its own precondition.** R3 as first written forbade every
  uncovered `RunEmit` (the provisional name, since retired for `Report`), the heartbeat included; the entry needed
  the seat kind in its condition.
- **A model's mutation can be the code's current behaviour.** `M_SEAT`, `M_ROUNDS` and now `M_EMITSEQ` are what the
  reference did, what the record's first draft said, and what the reference did again; each check was written so
  that the failing case names the thing it replaced.
- **The per-property modules are not a specification of the mechanism.** Fourteen modules each check one property
  over its own small abstraction; nothing a refinement could be *to* existed until `Mechanism.tla`, an operational
  model of `State::apply` written as a function from a projected state and an entry to the next state and the
  result. Trace validation then replays what the code did through that function (§15). The discriminators stay as
  what each test restates; the model is what the test's behaviour is checked against.
- **TLC's equality is typed.** It refuses `1 = "none"` rather than answering false, so a sentinel for an absent
  value cannot share a field with a number. Both failures on the way to the first validating run were this, and
  both were fixed by testing absence through domain membership and a boolean.
- **A model written from the code by the same hand agrees with the code.** Twenty-one traces matching on the first
  honest run is what that predicts, and is not evidence the code is right. What the harness buys is drift: a change
  to `apply` the model does not share fails at the exact step.
- **The invariants were provable, and cheap.** No module states liveness, and each property is a flag set at the
  action that would violate it or a set the property quantifies over, so the inductive step is the guard a mutation
  removes. The "Breaks under" column was in effect a list of which guard each proof would rest on. One invariant,
  `ContainedMeansConfined`, had to be invented: six clauses binding a lease to the guest generation it was granted
  against (`spec/proof-method.md`).
- **A proof is a second derivation of what a mutation breaks.** Each theorem takes the absence of the mutations that
  break it as a hypothesis, written apart from the binding table; the two disagreed in five places, and TLC rows
  run afterwards agreed with the proofs every time.
- **The prover sees what no model run reaches.** `NonComposition`'s NC1 needs that only admitted effects are
  recorded as via break-glass; the specification never reaches a state without it, so no TLC run could find the
  missing clause.
- **An unnamed `ASSUME` is a fact to TLC and nothing to the prover.** The non-vacuity facts the modules stated that
  way are now lemmas proved from the definitions, with witness records.
- **Some constants that look like premises are not.** The unread bounds hold for every `K` and `R`; `K < R` is what
  lets the bound refuse at all, which is non-vacuity, and stays TLC's. A counterexample's state count is not
  reproducible with every worker searching; its outcome is.

---

## 12. Where the argument is thin

The open list is G8. In narrative terms, the argument is weakest in sixteen places.

1. **The sandbox gap.** Effect exclusivity, ADR-0015's exhaustiveness, and ADR-0022 §6's confinement all rest on a
   mechanism that is now specified (ADR-0034) and not built. The reference issues every lease at rung 0; the first
   launcher is Proposed, and its first profile fails P3 on its face. Until a guest runs under an attested profile,
   the strongest claim TOPAK makes is an assertion. **This is still the single largest gap in the pattern**, and the
   record that closed its design half says so: only a mechanism can close the other.
2. **Correlated review failure.** Unanimity multiplies reviewers without making them independent. Floor fitness is
   the missing gate, and it is still unowned.
3. **Author-only ratification, and now assisted drafting.** Thirty-eight records were ratified by one person, and
   the pace has not slowed: the five batches of 2026.09.29 and the five of 2026.09.30 ratified seven records and
   eleven amendments in two days. Four records were drafted by the assistant at the custodian's request and settled
   by ratification, which is one step further from review than the rest; the fourth, ADR-0046, asked the custodian
   to regenerate its evidence so the digests would not be the drafter's alone, and the drafter ran it. Twenty-two
   carry confirmation markers and will be reviewed after bootstrap; the
   bootstrap set gets no confirmation promotion, by construction — confirmation runs under those records — and
   since ADR-0029 A2 it is instead reviewed at the bootstrap gate with the entire corpus. Until a reviewer is
   engaged, every review any record has received is the author's own.
4. **Anchor capture.** The residual is real, numeric, and the first line of any residual-risk statement.
5. **The archetype is unshipped.** Every theorem is about a configuration no one deploys, which is honest only if
   the declaration records are actually written. None has been.
6. **The archetype can grow without a bound on how.** Clause 4's admission test forces extension; the record that
   would constrain the direction of that growth is deferred (§8.2).
7. **Checks are evidence, not attestation, and proofs are of the model.** Fourteen TLA+ modules, an operational
   model with a trace harness, the floor gates and a running reference now exist, and every mutation fails as it
   should. Since 2026.10.02 thirteen of the modules are also proved: every invariant they state holds of every
   behaviour of the module, for every constant their assumptions admit, under the hypothesis that the mutations
   which break it are absent (ADR-0046). That retires "TLC at these sizes is a discrimination test, not a proof" for
   the invariants and leaves it standing for the mutations and witnesses. It changes nothing else here: the proofs
   were written, checked and regenerated by the hand that wrote the records, the prover is trusted as written
   (T-0045-31), and **agreement among records, checks, proofs and code written by one hand is not independence**
   (ADR-0033). The
   trace harness makes the link between modules and code mechanized for the first time, and ADR-0045 T-0045-28 says
   what it is not: a refinement.
8. **No floor is ratified.** The machinery that checks a floor is accepted; the genesis floor itself is a draft that
   passes the gates. Whether it is the *right* floor is floor fitness again (item 2).
9. **The replicas are trusted.** The mechanism's consensus replicas are crash-recovery, not Byzantine (ADR-0033 §3).
   Agents stay Byzantine at every position, but a compromised replica could propose an admit no floor ever
   evaluated, and the apply-time checks stop stale admits, not forged ones. ADR-0045 makes the replica set a
   trust-root row with the forged admit as its residual and mutual authentication as a delegated mitigation, and
   declines to require BFT; the authentication is still unbuilt.
10. **The independence criterion's arithmetic is the custodian's own.** ADR-0035's bounded share was designed on
    2026.09.28 to repair a claim the rehearsal had refuted, and nobody has compared it with how training-corpus
    overlap is measured in practice. The record marks itself confirmation-required for that reason and makes the
    review a ratification condition. It also declares that a pair whose rounds read more than they train on can
    dilute the bound, and that only the behavioral test can see it.
11. **Rung 1 trusts the operator.** The only cage the corpus has designed puts the person who runs the launcher, the
    launcher script and the container runtime in the trusted base for guest integrity, by ADR-0034's own table. That
    is honest and it is not much; rung 3 is the archetype because it is the first rung at which the host can only
    subtract, and nobody has built it.
12. **Collusion is uncovered.** Coupling separates a present, keeping-up Observer from an absent one and cannot
    separate an honest one from a colluding one; every fact it reads is the Observer's own assertion. Lineage
    independence is the only cover, it is unbuilt in the reference, and the correlated-miss test that would measure it
    has never run (§5.4).
13. **The coupling numbers are placeholders.** `T_obs`, `K` and Run's `R` were chosen for order of magnitude so the
    runs had values. No Observer has been measured, and a deployment that ships them unexamined is declaring them.
14. **The correlator reads everything and computes nothing yet.** It has a seat kind, a placement rule, a veto seat and
    a stated read set, and no detection function; it is the corpus's answer to the strongest published impossibility
    result, and it is still, in that respect, a noun (§5.1).
15. **The checker is trusted as written, and the gate evidence is unsigned.** Every floor change routed before
    2026.10.01 rested on a cvc5 answer nobody checked; since then a `holds` counts only with a proof the pinned
    checker accepted, and the trust has moved to the checker's rule signature, read as cvc5's authors wrote it, and
    to cedar's own folding of the totality gate, which never reaches the solver (§3.1). Every promotion vote still
    binds to a gate-evidence digest an operator asserted; the gate runner's key under ADR-0025 §1 (f) is the repair
    and is unissued (§7.9).
16. **What runs is not what is proved.** The modules' invariants are proved and their mutations checked at small
    constants; the Rust is asserted to follow them, and since 2026.09.30 shown to agree with a model of itself on every
    tested path, which is a harness and not a refinement. A proof of a module makes the refinement's target precise
    and does nothing else for it. The implementation, the model checker, the prover and the build toolchain are trust
    roots for every deployment,
    and the reproducible build that would fix the last one's identity is not declared (§7.9, §15).

---

## 13. Assumptions of use

The boundary register's highest-leverage fix was to put assumptions of use at the front, framed as a safety element
out of context. This is that list. **A deployment that does not meet these does not inherit the theorems.**

| # | Assumption | If it does not hold |
|---|---|---|
| **A1** | **Effect exclusivity is enforced by a declared, attested confinement profile** at rung 1 or above (ADR-0034), not asserted: no shell, no network egress, no filesystem outside workspace and corpus root, no path to the artifactory except `Submit` | `Contained` has no members; every containment theorem is void, and the enumeration in §4.1 is falsified rather than weakened. At rung 3 the assumption becomes a claim resting on named, audited components |
| **A2** | **Every allowlisted tool is hermetic** — no network, no filesystem outside the workspace, deterministic given its inputs | One tool with a socket collapses the alphabet to a single variant and makes the envelope vacuous |
| **A3** | **The anchor's key-holders are honest at the declared capture threshold** | A coalition at that threshold issues any floor-conformant rules. No safety theorem covers anchor intent |
| **A4** | **Grant seats review independently**, against evidence not derived from the author's artifacts | Unanimous reviewers reading the same vacuous gate output fail together; the quorum multiplies signatures, not judgment |
| **A5** | **A trained, authorized human is present** for break-glass, quarantine release, and the detection interval `D` | The HITL and HOTL postures degrade to unattended operation, which the pattern does not model |
| **A6** | **Trusted time exists** for every interval whose failure preserves authority — a break-glass TTL, Persona expiry (ADR-0032 §2). Re-attestation no longer needs it: it is triggered by renewal, not by an interval (ADR-0034 §3.6). `T_persona` (ADR-0031 A2) bounds the declared `ttl` and does not remove this assumption for the interval itself (§10) | Those intervals can be stretched by a slow clock. Intervals that subtract authority need only local monotonic clocks, and no clock failure costs containment |
| **A7** | **The deployment declares its degeneracies**, with kind, type changes, and a composition note | The deployment's theorem inventory is unknown, and conformance claims are unfounded |
| **A8** | **Confirmation-required records are cited as author-ratified** until a first quorum confirms them | A publication overstates eleven records, including both privileged-path records, the floor language, the lease, the exhaustiveness claim, and confinement |
| **A11** | **The lineage-independence criterion is in force**, with its thresholds set from measurements at training scale, before any deployment is declared at archetype provenance (ADR-0035) | Archetype provenance is a description, not a declaration; `Contained` has no members, whatever the rung |
| **A9** | **The mechanism's replicas are not compromised** — crash-recovery, authenticated to one another (ADR-0033 §3; ADR-0045 T-0045-1) | A Byzantine replica can propose admits no floor evaluated; the apply-time re-check does not re-run the floor |
| **A10** | **Each effect class declares `T_irrev`**, and `W + L + D < T_irrev` holds for it (ADR-0032 §4) | The HOTL posture has no budget; an effect irreversible on emission must be removed from the alphabet |
| **A12** | **Every Run Thinker's cell Observer keeps up**: heartbeats within `T_obs`, watermark within `K`, coverage to each seal (ADR-0039) | Nothing is lost to safety. The Thinker's admits and its next round stall, and a deployment that will not accept the stall declares D-0039-1 and detection fails open |
| **A13** | **The cell Observer is not colluding with its Thinker**, which lineage independence is the only structural cover for (ADR-0039 §5) | Every liveness fact is the Observer's own assertion; detection fails open against the one case coupling cannot see, and the residual-risk statement must say so |
| **A14** | **The deployment declares its trusted base** under ADR-0045's schema, instantiating the archetype's rows and adding none that are not degeneracies, and every component it relies on is a row of some class | An undeclared row is false: the deployment sits at the bottom of every axis whose theorems rest on it (D-0045-1). Four of the assumptions above, A2, A3, A6 and A9, are rows read as a checklist |

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
bundle → consensus-ordered admit → effect, for Build's six actions and Run's three (§2.9). Each letter is filled by
one instrument, by role:

| Letter | Instrument at the reference |
|---|---|
| **T** | TLA+ unchanged; its properties restated as Rust tests with the same mutations, and since 2026.09.30 every tested behaviour replayed through `Mechanism.tla` |
| **O** | Cedar, linked, with the gated floor compiled in by path and refused at startup unless its bytes match the gated digests; OPA sidecar with an in-process WASM fallback bound to the lease's revision |
| **P** | Sans-IO Multi-Paxos, `Voting` under message-level `Paxos`, driven by a deterministic simulation |
| **A** | The alphabet as MCP tools, and nothing else |
| **K** | Kafka, one topic per principal per round, emissions after commit, denials unordered |

**What it is not.** It is **evidence, not the verified object** (ADR-0033 §1) — the same kind of evidence as a TLA+
check, cited by a manifest digest and a commit, with the claim scoped to what its tests check. It has never been
promoted, no promotion pipeline exists to promote it, and nothing in it is in any TCB. It is not a deployment: every
lease it issues is rung 0, so every principal it serves is `Mediated`, and it fails assumption of use A1. **A running
program invites being mistaken for the mechanism**, and this paragraph exists because saying so once is not enough.

**It moved once since revision 7**, again at revision 9, and four times since. Batch 10 made the reference refuse
a renewal that changes the confinement rung (ADR-0031 A1), and a second addendum cited it. On 2026.09.29 it followed
three records at once: seat kinds and one seat per principal at the grant (ADR-0037), cells and a correlator on the
veto roster (ADR-0038), and heartbeats, marks, seals, `live(o)` at decide and apply, the cross-round grant and
coverage at the tally (ADR-0039), with the values file compiled in beside the floor (ADR-0033 A2, Batch 16). The same
evening it took Run's alphabet while the records were still Proposed: three Run tools on the front door, a second
pinned set for `Consult`, the effect counter, the `Actuate` record with its `unknown` outcome ahead of the seal, and
a refused abstain, twenty-four files, fifty-five tests, and the first addendum whose records were all Proposed
(ADR-0033 A3, Batch 17; the records followed on 09.30 and the addendum needed no revision). Then the values pin for
`T_persona` with no behaviour change (A4, Batch 19), and the trace recorder (A5, Batch 21, below). On 2026.10.01 it
built Batch 17's three debts (A6, Batch 23): the `ttl` bound refused at grant and at every renewal, the two key
fields in the issued rules, and a bundle loaded only under a signature that verifies against those keys, with a
renamed tarball under a forged manifest refused by test; eighteen files, 381 lines, sixty-one tests. The register
stands at thirty-four assumptions and eighteen gaps; the bundle-signing gap retired, and the newest gap is still
channel fidelity, G19, which nothing checks.

**What it showed.** The records compose, subject to what it does not show (below): every link of §4.1's audit chain
has running code. Making them run took the assumptions and gaps above, each tagged in the code, which turns "the
mechanism will handle it" into a list. And it produced eleven findings about the records themselves, and on
2026.09.29 three more: the reference had enforced one live lease per *seat* where the records meant per *principal*;
a coupling rule written for every Run emission refused the heartbeat it depended on; and `T_obs` cannot be
re-checked at apply, because it is a per-replica clock, so only the deterministic half of liveness is.

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
channel, and the guest launcher that would make them the same pipe is designed (§2.7) and not built. Tool
hermeticity: tools are pinned by binary and schema digest and run in a cleared environment, and their behaviour is
unchecked; in Run, the channel a tool opens is declared and nobody checks it (G19). The Observer as a detector: the
reference seats one, hears its heartbeats and stalls on its absence, and the Observer that would produce a finding
is an e2e fixture with nothing behind it. `W(p)` as an ACL: cells are declared, not enforced. Bundle custody:
bundles verify under a dev key with custody (1, 0), and signing at promotion is not a pipeline step (G8, item 67).
The archive, erasure, masking, Persona attestation and bootstrap: none
is built. Scale and long-running behaviour: there are no snapshots, and every admit waits for a consensus round. And
that the floor is the right floor.

**What it is checked against, since 2026.09.30.** `spec/Mechanism.tla` is an operational model of the core's state
machine, one operator per log entry kind, written as a function from a projected state and an entry to the next
state and the result. When asked, the core records every `apply` as a step, and a driver replays each recorded
trace through the model in TLC, failing at the first step whose projected state or result differs. The first run
replayed every behaviour the mutation and e2e suites exercise, **21 traces and 163 applied entries, each step
matching**, over grants, renewals, revocations, fences, issuances, break-glass approvals, heartbeats, promotion
with coverage and Run sealing; the second, after Batch 17's debts changed the model, 22 traces and 168 entries, and
on the way it caught a test that lowered a floor constant between two entries, which the model cannot see without
an entry: the harness working as intended, on the test and not the code. Three facts the model takes from the trace rather than computing: whether an
issuance passed `validate_issuance`, whether a break-glass approval's signature verified, and whether an admit's
parameter digest matched. What it is: the first mechanized link between `spec/` and `mechanism/`, and a harness
that catches drift at the exact step. What it is not: a refinement, or independent evidence, since the model was
written from the code by the same hand on the same day; agreement was expected. ADR-0045 T-0045-28 stays a
trust-root row, and ADR-0033 owns the chain's next two stages, a Lean model with differential testing and then its
compilation.

**How it stays honest.** The reference pins the digest of every record and TLA+ module it follows, forty-four pins
now, and a test fails when one changes or when the code cites one that is not pinned (G3 §5). Every change to a
record in this revision's window was followed by a failing drift check, a review against the code, and a re-pin.
That is the discipline in miniature: the reference is not trusted to track the corpus; it is checked for it. The
trace harness extends the same discipline from the records to the behaviour.

---

## 16. The lineage rehearsal

ADR-0035 says the criterion must be rehearsed before it is ratified, and `slm/` is the rehearsal: small models
pre-trained from scratch on an M4, public corpora with their admission declarations, a projector that reads the
reference's log, and a gate suite over synthetic records. Its results files are the record, since its run
directories are not tracked, and G4 measures the tree by manifest.

**What it found, in order.**
- **The gate suite passes**: every clause E1–E5 fires alone at least once, the relation is irreflexive, symmetric and
  not transitive, E3 fails closed without a measurement or with an unpinned tool, and strength is weakest-link.
- **The overlap tool separates the cases by orders of magnitude, as shares.** FineWeb-Edu inside a FineWeb slice
  twelve times its size: 1.0000, the overlapping-corpora case ADR-0017 named, reproduced on real data. Two dumps of
  the same filtered crawl: 0.002. Filtered web against public-domain books: 0. Equal-size slices of the crawl and its
  filtered subset share about the filter's keep rate. The measurements are at 20 MB and are too small to set θ from;
  the thresholds come from slices at training size.
- **A lineage was projected from the reference's log** and matched its authored manifest, and three tampered
  manifests — an omitted object, a changed seed, an injected draft — were each *Contested* with the divergence
  attributed to a seat, lease and log slot. Rerun on 09.28 after the record gained its `consumed` set, with the same
  verdicts.
- **The record's soundness claim was false.** §2 said the projection could over-approximate what a round read and
  every rule would only get stricter. E3 and the distillation rule were shares *of* what was read, so charging a
  trainer with more corpus diluted them: 13 of 2,000 random E3 fails and 241 of 2,000 distillation fails turned into
  passes by adding ingress. The revision that leaned on that claim to bound projection by the cage was written the
  same day, without reading the check.
- **The repair is a bound, not a byte count.** Every share the gate computes is now an upper bound: numerators over
  what a round could have read, the denominator the smaller set of what it did read. The check holds over 2,000
  trials. An absolute-bytes rule would also have held, and would have been immune to a pair that reads more than it
  trains on; it was not taken, because the cases separate as shares and a byte threshold set at one corpus size says
  nothing at another. The padding case is declared as a residual, with its frequency measured: 24 of 2,000 for E3,
  250 of 2,000 for distillation.

**What it does not show.** That θ is right, that the near-duplicate tool is the right tool, that two lineages the
rule calls independent fail independently (only §6's test can), and that the bound is how anyone else measures
overlap. The last is why ADR-0035 R2 is marked for review before ratification (§12, item 10).

---

## Appendix H. Changes from revision 11

- **State of record repointed** from G7 to G8. Counts updated: forty records accepted, two in part, one superseded,
  three Proposed, twenty-two confirmation-required (§0, §9). Four assistant-drafted texts, all ratified, and
  ADR-0046's condition run by the drafter (§0, §9, §12).
- **§1:** the T role names proof beside model checking.
- **§7.9:** thirty-one rows; the prover beside the model checker among what runs; T-0045-31 as Batch 25's dependent
  entry, TLC's row bounding the mutations and witnesses only, and the binding table's proof column and five
  corrections.
- **§9:** ratification at 2026.10.02 and Batch 25; ADR-0046 in the confirmation-required list; the bootstrap
  trigger's two modules proved, with `GenesisSatisfiesFloor`'s shape as a lemma.
- **§11.1:** item 6, the proofs are of the specification; item 7, the corpus's own verifier and its row.
  **§11.2:** MAP 2.3 closed. **§11.3:** five bullets from the proofs.
- **§12:** the open list is G8; item 3 counts four assisted texts; item 7 says what the proofs retire and what they
  leave; item 16 says what runs is not what is proved.
- **§15:** a sentence revision 11 left standing, that bundle signing and Batch 17's two fields were unbuilt, is
  corrected: ADR-0033 A6 built them before G7, and what is not shown is the bundle key's custody.
- **Appendices A to G retained.**

---

## Appendix G. Changes from revision 10

- **State of record repointed** from G6 to G7. Counts updated: thirty-nine records accepted, two in part, one
  superseded, three Proposed, twenty-one confirmation-required (§0, §9). The three assistant-drafted texts are all
  ratified (§0, §9).
- **§2.6:** ADR-0045 cited as ratified.
- **§3.1:** the floor gated six times, the last with proofs; bundle signing implemented at the reference under a dev
  key (ADR-0033 A6); the trusted step at the gate
  is now checked: ADR-0030 A1 in force, the wrapper, the checker and its signature, what the checker does not reach,
  D-0030-2 as the position of a run without the checker. **§3.2:** what a wrong solver could do, past tense.
- **§7.8:** the trusted-base row's record no longer Proposed. **§7.9:** ADR-0045 ratified in Batch 22; the solver's
  row rewritten for the checker; "Not yet ratified" replaced by the binding table and the two rows that changed
  class since.
- **§8.2:** the trusted base no longer Proposed; D-0044-1, D-0045-1 and D-0030-2 moved out of the Proposed-or-pending
  clause and dated.
- **§9:** ratification at 2026.10.01; Batches 22 to 24; three debts struck from the face list; the trusted-base
  declaration in the genesis bundle now that ADR-0045 is in force.
- **§11.1:** item 7 names the checker. **§12:** item 15 rewritten, the checker trusted as written and the gate
  evidence still unsigned.
- **§15:** four moves since revision 9; the A6 addendum; the register at thirty-four and eighteen; the second trace
  run and what it caught; forty-four pins.
- **Appendices A to F retained.**

---

## Appendix F. Changes from revision 9

- **State of record repointed** from G5 to G6. Counts updated: thirty-eight records accepted, two in part, one
  superseded, four Proposed, twenty confirmation-required (§0, §9). The assistant-drafted records named in §0, §9
  and §12. A14 added (§13).
- **§2.4:** each domain's alphabet is its own; `Actuate` replaces `RunInvoke` in the seat-kind bound; Run's profile
  shaped by ADR-0042 §6.
- **§2.5:** the per-round TCB as the derived slice of ADR-0045's table; the `ttl` bound (ADR-0031 A2).
- **§2.6:** the per-rung table flattened to rows; the rung-0 run (ADR-0034 A1) and its finding.
- **New §2.9, Run's alphabet**, from ADR-0040 to ADR-0043: three variants, the carrier shared and no name, no
  terminal variant, the obligations by owner, confinement left Proposed, the checks, and the markings.
- **§3.1:** bundles signed under an issued key (ADR-0044); the solver as the one trusted step and ADR-0030 A1's
  repair; the floor at seventeen policies, gated five times, with `T_persona`. **§3.2:** what a wrong solver can do.
- **§4.1:** Run's effect variants. **§4.3:** ADR-0003 A3 scopes the storage clause.
- **§5.2:** ADR-0021 ratified (Batch 18). **§5.4:** the sequence counts effects; `Consult` exempt; `RunCoupling.tla`.
- **§7.2:** rules carry the keys that vouch (ADR-0025 A1). **§7.8** grows to fourteen layers: bundle and trusted base.
- **New §7.9, the trusted base declared**, from ADR-0045: the rule in ADR-0015's terms, three classes and a refusal,
  rows as premise nodes, the thirty rows, what applying the rule changed, the record's own correction.
- **§8.2:** the trusted base as an axis; five declarations added.
- **§9:** ratification at 2026.09.30; Batches 17 to 21; two records in part; the new kind of debt; the trusted-base
  declaration in the genesis bundle.
- **§10:** `T_persona` and the clock (ADR-0045 finding 2).
- **§11.1:** two items added, the refinement chain and the Dafny verifier. **§11.3:** four lessons from the trace
  harness; the retired name annotated.
- **§12** from fourteen weak places to sixteen: the solver and gate evidence; what runs is not what is checked.
  Items 3, 7 and 9 restated.
- **§15:** Run's three actions; three addenda since revision 9; the register at thirty-three and nineteen; what the
  reference is checked against; what it does not show, extended; forty-two pins.
- **Appendices A to E retained.**

---

## Appendix E. Changes from revision 8

- **State of record repointed** from G4 to G5. Counts updated: thirty-two records accepted, one superseded, fourteen
  confirmation-required, three of them for one amendment (§0, §9). A12 and A13 added (§13).
- **§1:** a principal holds exactly one seat.
- **§2.4:** alphabets bounded by seat kind (B10, B6); the Reader cannot hold `Draft`.
- **§2.5:** `principal` and `seat` determine each other; the reference's per-seat rule and `M_SEAT`.
- **§2.7:** a rung-0 grant may name a profile (ADR-0036 R1); the ladder; the host-run profile.
- **New §2.8, principals, seats and cells**, from ADR-0037: seats and stages, who forms the emission, retention at
  the archetype, the Reader's facts and the rung for conformance, one pair per cell, humans hold one seat.
- **§3.1:** the floor at sixteen policies and three files, gated three times.
- **§5.1 rewritten for ADR-0038**: scoping decided, ADR-0008 superseded; `W(p)`; what the correlator reads;
  placement on fault-domain grounds; any-of and no quorum; the veto roster. **§5.2:** coverage at the gate. **§5.3:**
  the Reader stage.
- **New §5.4, coupling**, from ADR-0039: heartbeat and watermark, `live(o)` in the strict form, R3 scoped to Thinkers,
  coverage across rounds at the grant, the correlator never coupled, collusion uncovered, break-glass coupled, the
  placeholders.
- **§6:** seat-binding values; ADR-0018 reversed in part.
- **§7.1:** veto seats re-homed; A2.2 and A2.3 as tally constants; A2 ratified in genesis.
- **§7.8** grows to twelve layers: seat and detection.
- **§8.2:** two axes added; the five Observer and retention degeneracies; the missing *properties lost* field.
  **§8.3:** ADR-0008 superseded; ADR-0018 added.
- **§10:** collusion on the residual-risk statement. **§11.2:** three gaps annotated.
- **§11.3:** five lessons from the 09.29 checks.
- **§12** from eleven weak places to fourteen: collusion, the placeholders, and the correlator as a noun. Item 3
  restated.
- **§15:** the reference's 09.29 change and third addendum; three findings that needed code; what it does not show,
  restated.
- **Appendices A to D retained.**

---

## Appendix D. Changes from revision 7

- **State of record repointed** from G3 to G4. Counts updated: thirty records accepted, eleven confirmation-required,
  three of them for one amendment (§0, §9). A11 added (§13); A1, A6 and A8 restated.
- **§2.3 rewritten for ADR-0034 §4:** `Contained` has four conjuncts, the fourth is the criterion, and it is
  unreachable for a different reason. Weakest-link provenance numbered by ADR-0035.
- **§2.4:** the hermeticity obligation owned for Wasm tools; the sandbox gap split into a closed design half and an
  open mechanism half.
- **§2.5:** renewal keeps the rung (ADR-0031 A1), with the silent-downgrade case that the records never met in a
  check; the C2 marking for A1.
- **New §2.6, confinement**, from ADR-0034: the failure-direction test, the rungs, the seven clauses, appraisal at
  grant, three verdicts, no silent downgrade at grant and renewal, the session key, the trusted base per rung, and
  what re-attestation does not detect.
- **New §2.7, the launcher**, from ADR-0036 (Proposed): the token outside the guest as the rung-1 binding, a profile
  that declares what it fails, the first profile failing P3, the node-side launcher as the second step.
- **§4.1:** the two positions still identical in strength, with the design half now existing.
- **§6:** lineage as a projection (ADR-0035, Proposed), the exclusion rule, the bound, and where it is enforced.
- **§7.8** grows to ten layers: confinement and lineage.
- **§8.2:** two axes added; the four-orderings warning; the D-0034, D-0035 and D-0036 entries.
- **§10:** `Contained` has no members, with the conditions for a first member.
- **§11.3:** three lessons: an omitted path, evidence that must match the measurement, and a check that refuted a
  record faster than a review.
- **§12** from nine weak places to eleven: the criterion's arithmetic, and rung 1 trusting the operator. Items 1 and
  3 restated.
- **§15:** the reference's one change since revision 7 and the second addendum; assumption count.
- **New §16, the lineage rehearsal.**
- **Appendices A, B and C retained.**

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
- **Scrub pass (2026.09.25).** §4.1's "strictly stronger than Moon & Varshney" conditioned on ADR-0022 §6's
  discharge, tracking ADR-0015 E2; until confinement is enforced the two positions are identical in strength
  (09.16 review, CR-1). Revisions 5 and 6 keep the old sentence as frozen cuts.
- **Amendment pass (2026.09.25, ADR-0029 A2 ratified).** §9's exception, trigger, ceremony and cleanup passages,
  §7.1's author-ratified note on ADR-0024, and §12 item 3 rewritten: the entire corpus is independently reviewed
  as a precondition of bootstrap, and the genesis bundle carries the review attestation. The marker exclusion for
  the bootstrap set stands; the no-review consequence is reversed.

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
