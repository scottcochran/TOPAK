# TOPAK — Theory of Operation

**Checkpoint 2026.09.15** · revision 4 (sweep; decompositions of 0025 and 0013; genesis middle path; **0029 ratified**; rules-floor non-vacuity run) · corpus manifest v1: `topak-genesis-corpus-manifest-v1-2026.09.15.md` · supersedes 2026.09.12 · *The Gripping Hand*

**Previous checkpoint:** "Theory of Operations checkpoint from ADR review" (2026.09.12).

This checkpoint consolidates fifteen sessions. In that window:
- five Architecture Decision Records (ADRs) were ratified (the Persona series);
- six more were drafted;
- the deployment ladder was replaced by a degeneracy lattice;
- the authority chain was closed at a single axiom.

**Sessions since 09.12**
- External assessment against Moon & Varshney and the NIST Playbook (09.12)
- NIST AI RMF Playbook delta inventory (09.12)
- MANAGE 3.2 / Persona series (09.12)
- Build gaps (09.12)
- Logprobs and interpretability (09.13)
- Boundary register (09.13)
- Boundary register assessment (09.13)
- Semantic containment boundaries (09.13)
- Archetype event-log immutability (09.13)
- Archetype Observer hierarchy (09.13)
- Floor rollout and chicken-and-egg (09.13)
- Build and Run vocabulary (09.13)
- Archetype and degenerate rungs (09.13)
- TLA+ Paxos cheat sheet (09.13)
- Feature list, promotion quorum, and trust anchor (09.15)

---

## 0. The ledger

| 2026.09.12 | 2026.09.15 |
|---|---|
| Model unpinned; MANAGE 3.2 the sharpest gap | **Accepted** (0016–0020). The Persona is the verified model artifact, provenance is recorded, and the lift is split into a decoder and a validator. |
| Build's membrane has no effect stream and no alphabet | **Proposed** (0021, 0022). A typed six-variant alphabet; the confinement obligation is stated but not discharged. |
| Deployment profiles as a ladder; axis unresolved | **Replaced.** Degeneracy lattice (0023, Proposed). A deployment is a tuple; the archetype is the unique maximum. |
| Promotion gate is a human signing key | **Proposed** (0024). Unanimous quorum of principals, with a veto seat for the Observer. |
| Regress terminates at axioms + the verified floor | **Proposed** (0025). The trust anchor is a havoc issuer. Intent is the sole axiom. The rules floor joins the verified object (0026); genesis rules are resident (0027). |
| Evictability test: "if you can be evicted, you are a principal" | **Restated** (0002 amendment, drafted). "Evictable **by an authority other than itself**." |
| Monotonicity at three layers | **Five layers** (§5.4). |
| ADR numbering: 0016/0017 collision | **Settled** by this checkpoint (§1). |
| `Contain` "hard rule enforcement" | **Renamed in substance.** *Boundary-enforceable containment*: two conjuncts, one proved and one assumed. |

---

## 1. Numbering, settled

Two sessions on 09.12 each assigned 0016 and 0017. This checkpoint records the resolution already
used by 0023 and later records.

| Number | Record | Origin |
|---|---|---|
| 0016–0020 | Persona series | MANAGE 3.2 session; ratified same session |
| **0021** | Build effect stream | Build gaps session, drafted as "0016" |
| **0022** | Build action alphabet | Build gaps session, drafted as "0017" |
| 0023 | Degeneracy | Degenerate rungs session |
| 0024, 0025 | Promotion quorum, trust anchor | 09.15 |

No ratified record was renumbered. The Build drafts were Proposed, so the no-renumbering rule is
intact.

**Sweep item:** 0022's text still cites "ADR-0016" (read as 0021). It also cites "ADR-0005's split"
for `Contained`/`Mediated`; that split originates in 09.12 checkpoint §5, not in 0005.

---

## 2. The model is pinned: Persona series (0016–0020, Accepted)

From the MANAGE 3.2 session. The 09.12 inventory's sharpest asymmetry was that everything was
pinned except the model. That asymmetry is closed.

- **0016 — Persona.** A verified artifact binding a model to its complete runtime configuration:
  - provenance and cryptographic identity;
  - system prompt and decoding parameters;
  - decoder identity and hash;
  - decode-observability class;
  - seat binding.

  Replay scope was split out before ratification.
- **0017 — Archetype admits only in-house pre-trained Personas**, requiring two independent
  lineages. Ratified with its **independent-lineage criterion outstanding and assigned**: overlapping
  public corpora do not count as independent.
- **0018 — The typed lift splits.** The model-specific decoder ships inside the Persona; the
  model-agnostic validator lives in the mechanism. This is the third instance of the ADR-0010 move
  (verified core, parameterized edge), this time applied to syntax.
- **0019 — Optional decode observability, narrow form.** `none` is the only unconditional value.
  `topk_logprobs` is admissible for decoding conformance and substitution detection only, and
  **never** in any claim about Observer detection latency `L`.
- **0020 — Replay scope is boundary events only**, with explicit revisit triggers. Replay
  reconstructs what crossed the membrane, not what happened inside it.

**Consequences carried**

- Havoc still makes a *worse* model harmless for containment. Silent substitution is now a
  detectable identity mismatch rather than an unmodeled event.
- None of 0016–0020 adds to ADR-0013's carve-out count. Revocation, decoder failure, and rung
  subtraction are all denies.
- **Open:** raw-emission retention sits between 0003 and 0006. ADR-0013's forensic floor must now
  account for boundary-only replay.

**From the logprobs session.** Interpretability can make `L` measurable, but only statistically,
which changes the shape of the safety argument from hard bound to confidence bound. White-box
Observers also increase model-family coupling, which cuts against the cross-family Observer
requirement. 0019's narrow form is the guard against drifting there by accident.

---

## 3. Build gets a surface (0021, 0022, Proposed)

From the Build gaps session, with the 09.15 revision.

**0021 — Build effect stream.** The question reframed to "does Build have an Observer at all."
Option A was chosen: reuse 0003's round-topic scheme, with a Build round defined as one pipeline
invocation. Retention horizon, not broker pressure, is the real divergence from Run. Blocked on 0022.

**0022 — Build action alphabet.** Egress only. The action variants:

| Variant | Effect |
|---|---|
| `Read` | Read from the pinned corpus |
| `Draft` | Write into the round workspace |
| `Invoke` | Run a tool on the allowlist (name plus digest) |
| `Emit` | Emit to the Build effect stream |
| `Submit` | Terminal submission for promotion |
| `Vote` | Promotion vote (added 09.15, per 0024) |

There are three mechanism parameters: corpus root, tool allowlist, round bound.

- **§6, the confinement obligation, is stated and not delivered.** No shell, no egress, no path to
  the artifactory except `Submit`. Until it is discharged, Build principals are `Mediated`.
- **`Invoke` is the whole attack surface.** One allowlisted tool with a socket collapses the
  envelope to vacuity. The per-tool hermeticity obligation is unowned.
- **Capability cost.** This alphabet is not how agents write code today: no shell, no package
  manager, no git. Say so in the article.
- **Evidence on the floor question.** Build and Run have partially disjoint alphabets, so "one
  shared floor" is either vacuous or two floors under one name. Per-class floors with a shared
  verified core fit better. The same question now applies to the rules floor.

**From the Build/Run vocabulary session.** Developers and pipelines do **not** get separate
principal types; that would re-privilege humans against the universal principal type.
- **Hermetic build steps** are claimable as `Contained` by construction.
- **Weakest-link provenance rule** (candidate ADR, unnumbered): any provenance chain containing a
  `Mediated` principal yields attribution, not a safety property. After 0024, every promotion chain
  contains `Mediated` voters, so promotion provenance is attribution, consistent with 0024's stated
  consequence.
- **Homonym risk:** lease and epoch mean slightly different things in Build and Run. Glossary item.

**HITL on every action** (thought experiment, not a decision). Build loses its interior, and review
fails at action cadence the same way it fails at pipeline cadence. Break-glass also loses its
contrast with the normal path. HITL on every action requires 0022 rather than replacing it.

---

## 4. From ladder to lattice: degeneracy (0023, Proposed)

Three demotion proposals arrived on three different parameters within 48 hours:
- Persona provenance;
- event-log legibility;
- Observer scoping.

They are not mutually comparable. Two of them reversed accepted records. The ladder was only ever
true on one axis.

### 4.1 The relation

- **Degeneracy.** D is a degenerate form of archetype A if D is obtained by driving named
  parameters to limiting values. *Degenerate* is the formal register; *reduced* is the operational
  one.
- **Effect is premise loss, not weakening.** Theorems are present or absent. There is no partial
  credit.
- **The archetype is the unique maximum of the parameter lattice.** It is a reference point, not
  necessarily shippable. ISO 26262 safety-element-out-of-context is the precedent.
- **Admission test.** A variation is a rung only if it is reachable from A by parameter limit. If
  it holds a capability A lacks, **A is incomplete**, and rejection is a finding about the archetype.
- **Rungs are per-axis.** A deployment is a tuple. Unqualified "rung demotion" is barred.
- **Declaration records are mandatory; mitigation is optional.** Fixed schema:
  - parameter;
  - archetype value;
  - deployed value;
  - premises falsified;
  - theorems voided;
  - mitigation (optional);
  - composition note (mandatory above one parameter).

### 4.2 Reversals in effect

- **ADR-0008** (Observer scoping). The archetype proposal is per-principal Observers **plus a
  cross-principal correlator**. Shared-only is not a degeneracy of per-principal Observers, because
  it gains cross-principal visibility; the archetype had to grow the correlator first. The strongest
  argument is bounded `L` and injection blast radius, not independence of judgment. **A superseding
  record is required.**
- **ADR-0017's ordering-primacy clause.** Provenance as *the* deployment axis is reversed by
  per-axis rungs. The admission clause stands. **Supersession of that clause is required.**

### 4.3 Event-log legibility replaces immutability

From the log-immutability session.
- **"Immutable" is the wrong property.** It lets a deployment claim conformance after
  erasing evidence (ADR-0006: sealed round-topic and plaintext-store deletion).
- **The archetype property is legibility:** every admitted boundary event remains readable by the
  declared audit authority for the declared horizon.
- **HIPAA subtracts the record** (erasure). **SCI subtracts the reader set** (compartmentation), and
  is archetype-conformant except at spill remediation.
- **The archetype log is the maximum projection** from which each compliance regime derives.
  HIPAA's additive requirements (disclosure accounting, six-year retention) would be inexpressible
  under subtraction-only.
- **This supersedes the 09.12 framing** of HIPAA and SCI as maximal assurance targets.

### 4.4 Pending declaration records (unnumbered)

| Record | Status |
|---|---|
| Provenance demotion | Pending |
| Legibility demotion | Pending |
| Observer scoping demotion | Pending; follows the 0008 supersession |

Records drafted 09.15:
- **D-0024-1** k-of-n promotion; **D-0024-2** single signer.
- **D-0025-1** TUF-style threshold anchor; **D-0025-2** n−1 eviction with replacement.

### 4.5 Known gaps in 0023 itself

- **Composition** is assigned to ADR-0013, which has no owner.
- **The parameter set is not enumerated**, and chain finiteness is unproven.
- **The admission test must check for type changes, not only voided theorems** (found 09.15). A
  degeneracy can move a participant from the gate to principal, which moves the gate and changes the
  trusted computing base (TCB).
- **Archetype versioning is needed.** The archetype grows on failed admission. Conformance must bind
  to (archetype version, rung tuple), and published versions freeze.
- **Register risk.** "Degenerate" collides mildly with TLA+'s "degenerate behavior." Glossary item.

---

## 5. The authority chain closes (0024, 0025, Proposed rev. 2)

### 5.1 Promotion is a unanimous quorum (0024)

The single signing key was the last privileged human grant.
- **Unanimity rule.** Promotion requires unanimous grant votes from human `Mediated` grant seats,
  with no deny from veto seats.
- **Veto seats.** Held by the independent Observer group (ADR-0008). Admissible only to deny,
  per ADR-0007.
- **Veto-seat silence is not a veto.** Requiring a "no finding" attestation would make judgment an
  enabling condition.
- **Binding.** Votes bind to (artifact digest, gate-evidence digest, rules epoch). Rules-epoch
  changes fence in-flight votes.
- **Gates enable voting; they do not vote.**
- **Author recusal.**
- **Runtime subtraction is not promotion.** E-stop, lease expiry, and `deny=all` stay local.

**Not fixed:** correlated review failure. Unanimous humans reading the same vacuous gate output fail
together (Moon & Varshney §4.6; Knight & Leveson). Floor fitness and MEASURE 2.13 remain open.

### 5.2 The trust anchor is a havoc issuer (0025)

Three treatments were weighed:
- **(A) Infallible:** oracle.
- **(B) Havoc:** any authentic issuance, bounded by a verified floor.
- **(C) Characterized:** composition modeled.

Under B, composition never enters the proof. The decision is **B, with infallibility split three
ways**:

| Property | Treatment |
|---|---|
| **Intent** | **ASSUMED**, the sole axiom: *an authentic issuance at the current anchor epoch is what the anchor intended* |
| **Integrity** | **MODELED**: `Issue` is a havoc environment action bounded by an opaque `Authentic`, epoch increment, and the **rules floor** |
| **Custody** | **DECLARED** per rung: (capture threshold, loss tolerance) |

**Rules** are the authority-defining set:
- promotion roster and its parameters;
- break-glass and erasure rosters;
- the anchor key set;
- floor relaxation and new exceptions.

Floor tightening is an ordinary promotion. Rules are bounded by the **rules floor (ADR-0026)**. Genesis rules are resident on 0012's argument (**ADR-0027**). Both were split out of 0025 by the decomposition test (§5.7).

**Custody axis (anchor recoverability):**

| Record | Custody model | (capture threshold, loss tolerance) |
|---|---|---|
| Archetype | Strict unanimity | (n, 0) |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) |
| D-0025-1 | TUF-style threshold | (k, n−k) |
| — | Single custodian | (1, 0) |

- **Archetype failure mode.** Loss freezes the rules; the only exit is **re-genesis**, which creates
  a successor system rather than continuing this one.
- **Dominance rule.** The archetype moves only to Pareto-dominating pairs.
- **The axiom does not grow.** A non-increasing TCB across archetype versions is a tracked property.

**Asymmetry worth stating in the article:**
- Degrading the promotion quorum changes the rules floor, so it is a **mechanism release** and
  reopens proofs.
- Degrading anchor custody instantiates `Authentic`, so it is a **declaration** and reopens nothing.

### 5.3 Evictability test, restated

> **A principal is anything evictable by an authority other than itself. Whatever is not is at the
> gate.** Resignation is not eviction.

- **Archetype.** Anchor key-holders sit at the gate. They are attributable non-principals, with
  `Mediated` applied as attribution only.
- **Degenerate custody rungs.** Key-holders become principals.
- **Promotion voters** are principals on every rung.
- **SUT vs system-testing.** From the floor-rollout session: the system-under-test versus
  system-testing cut runs *inside* each domain, and the restated test is its carrier at B14. Casting
  Build as the test apparatus would invert the trust relation that 0010 refused.

### 5.4 Monotonicity, now at five layers

| Layer | Statement | Source |
|---|---|---|
| Decision | Consensus for grants, local for denials | Established |
| Policy | Bundles only subtract from the floor | ADR-0010 |
| Change | Authority-increasing changes need consensus; decreasing ones are local and attributed | Floor-rollout session, 09.13 |
| Deployment | Degenerate forms lose theorems, never gain capability | ADR-0023 |
| Authority | Relaxing rules needs the anchor; operating within them does not | ADR-0025 |

**At the pattern level this inverts.** Tightening the archetype puts every conformant deployment into
declaration debt. Relaxing it voids published theorems. Both directions cost something.

### 5.5 Floor rollout (09.13, now absorbed)

- **Floor rollout is mechanism release.** The floor is embedded in the verified object, so these are
  not separate protocols.
- **The recursion terminates safely at floor₀ = default-deny only under tighten-only semantics.**
- **Relaxation needs separate authority.** Supplied by 0025, and written into 0010 by amendment.
- **Stop attribution is non-erasable.** It is a feedback path, not just evidence. The Observer is a
  controller in STPA terms, not a probe.
- **ADR-0006's scope is a data class, not a store.**

### 5.6 Drafted changes to other records (09.15)

**Test for amending an accepted record:** amend only where its decision text becomes **false**.

| Record | Change | Kind |
|---|---|---|
| 0002 | A1 gate text superseded (trigger 0024+0025); **A2 evictability test restated (standalone)** | Amendment (accepted record) |
| 0003 | Seven clauses annotated; four independently supersedable; no split | Clause annotation |
| 0007 | §4.2 → §4.6 and Appendix B | Erratum |
| 0010 | A1 verified object adds rules floor; A2 floor-change direction (trigger 0026); §4.2 citation | Amendment + erratum |
| 0017 | SLSA / in-toto citation for provenance ordering | Erratum |
| 0015 | Adds exhaustive authority-change set {promotion, anchor issuance}. The audit chain ends at the 0025 axiom. | Revision (pending) |
| 0022 | Adds `Vote`; author and voter disjoint; `Issue` outside Build; reference errata | Revision (pending) |
| 0024 | Quorum parameters read from issued rules, bounded by 0026 R1–R3; timeout-never-grants is a mechanism constant | Revision (pending) |

### 5.7 Decomposition of ADR-0025 (09.15)

Revision 2 bundled eight clauses. The test, *can this clause be superseded alone?*, split it:

| Clause | Result |
|---|---|
| Sole issuer; three-way split | **Stays in 0025.** Neither is meaningful without the other. |
| Rules floor | **ADR-0026.** Also receives 0024's archetype values, so promotion degeneracies change 0026, not 0024. |
| Genesis rules resident | **ADR-0027.** Same independence 0012 had from 0010. |
| Evictability test | **0002 Amendment 2, standalone.** |
| Issuance ordering; non-erasure | 0015 revision; 0013 scope |
| Dominance rule; non-increasing TCB | 0023 scope |
| Custody declarations | Annex records A-0025, D-0025-1, D-0025-2. Separately supersedable by construction. |

**New distinction from ADR-0026:** tightening the *policy* floor is one key (promotion), but
tightening the *rules* floor is two keys, because it constrains the anchor, which must consent.

Everything else is carried as scope on the face of 0024 and 0025. ADR-0013 gains four
non-composition cases:
- break-glass × erasure (existing);
- break-glass × promotion;
- break-glass × issuance;
- erasure × vote and issuance records.

ADR-0014 narrows to proposal eligibility.

---

## 6. Boundaries and what `Contain` actually claims

### 6.1 `Contain` is boundary-enforceable containment

From the semantic-containment session. "Semantic containment" collides with 0007's semantic-lift
definition and asserts the opposite of the design.

`Contain` is **two conjuncts of one formal statement**:
1. A **proved** boundary-enforceable property class, over vocabulary and envelope, by mechanical
   extraction.
2. **Effect exclusivity**, assumed and operationally discharged. ADR-0015 is the instrument, and it
   is unratified.

The two instantiations rest on different audited substrates. Run uses the paper's deployment stack.
Build rests on trusting-trust and SLSA concerns. The paper's Figure 1 covers Run only, so either a
second diagram or an explicit acknowledgment is needed.

### 6.2 Boundary register (09.13)

Fourteen boundaries, each with four columns: cadence, instant, interval of untruth, and behavior
under unavailability.

- **B8, Persona evolution**, is the most critical: an uncontrolled outer cadence with no instant.
  Apple Private Cloud Compute is a shipped counterexample showing it can be controlled.
- **Break-glass grants lack TTL expiry.** That breaks the monotonicity claim. Now also a 0025 rules
  item, since the break-glass roster is anchor-issued.
- **The clock model is unstated.** It underlies leases, fencing, and now vote timeouts. The
  assessment notes Gray/Cheriton leases and RFC 9334 give a standard answer, so this is **open with
  a known answer**, not open.
- **`Contained` may have no members** while the sandbox gap stands.

### 6.3 Register assessment (09.13)

**Good**
- The unavailability column and cadence as a first-class axis.
- The CALM result.
- The †-marking and read-by-holes method.

**Bad**
- No per-boundary adversary model.
- B5 is unnamed as a declassification boundary.
- 0017's provenance axis re-derives SLSA without citing it.
- Fail-closed uniformity is presented as costless.
- No owner column; B14 has no owner.

**Ugly**
- B8 has a shipped counterexample.
- `Contained` possibly empty, and buried late in the document.
- Independence is empirically weak (Knight & Leveson).
- No timing budget for what is effectively a real-time safety architecture.

**Highest-leverage fix:** move **assumptions of use to the front**, framed as ISO 26262 safety
element out of context. That converts the largest weaknesses from omissions into declared
conformance.

---

## 7. External alignment

### 7.1 Moon & Varshney (arXiv:2605.09045v2)

**Concordances**
- Havoc semantics.
- The containment/oracle split.
- 0007 matches their boundary-enforceable property class.

**Extension:** 0010's floor plus refinement. The paper never addresses policy change cadence.

**Exposures**

| # | Exposure | Status |
|---|---|---|
| 1 | Citing §4.2 for a result in §4.6 and Appendix B | **Errata drafted** (0007, 0010) |
| 2 | Three gates are insufficient by their published result; a **fourth gate, floor fitness**, is required | Unowned; this is MEASURE 2.13 |
| 3 | Sandbox gap, reframeable in the paper's deployment-stack vocabulary | Open |
| 4 | Theorem vs corollary misalignment in the `Contained`/`Mediated` split | Open |

**Spelling:** the co-author is **Varshney**. Swept 09.15: no misspelling in any artifact available this session. Check any draft outside the Project before publishing.

### 7.2 NIST AI RMF Playbook

Two artifacts:
- the 09.12 **delta inventory** (all 72 subcategories);
- the 09.15 **feature list**: 48 features under eight principles, each with Playbook correspondence
  and the unaddressed practices.

**Recount.** The inventory's stated tally was wrong. The row marks give:

| Mark | Count |
|---|---|
| Met | 6 |
| Partial | 12 |
| Convertible | 15 |
| Gap | 9 |
| Excluded | 30 |
| Contradiction | 1 |

(MEASURE has 22 subcategories; MANAGE 1.4 was dropped from the gap list.)

**Movement since 09.12, pending the next inventory pass**

| Subcategory | Change |
|---|---|
| MANAGE 3.2 | G → likely P or M (Persona series) |
| GOVERN 6.2 | G, narrowed (archetype excludes external models) |
| GOVERN 3.2 | M, strengthened (0024, restated test) |
| GOVERN 2.3 | G → P once grant seats and anchor custody have named roles |
| GOVERN 1.5 | P, gains a review owner (anchor) |
| GOVERN 1.7 | P, gains a system-level decommission event (re-genesis) |
| GOVERN 1.3 / MAP 1.5 | C, the axis question is resolved by 0023 |
| MANAGE 2.4 (!) | Resolution sharpened: legibility, non-erasable stop attribution, votes and issuances in the forensic floor |

**Unchanged gaps:**
- MAP 2.3 (TLC vs TLAPS undeclared)
- MAP 3.4 (operator proficiency)
- MEASURE 2.13 (floor fitness)
- MEASURE 3.2 (`L`)
- MANAGE 1.4 (residual-risk statement)
- MANAGE 3.1 (monoculture)

### 7.3 TLA+ practice (cheat-sheet session)

- **`Voting` is a mandatory abstraction layer** between `Consensus` and `Paxos`.
- **`ENABLED Deny(a)` is a mechanically checkable invariant** for consensus-for-grants and
  local-for-denials.
- **HITL, HOTL, and HOOTL are `ENABLED` predicates.**
- **`W < L < D` is only partly expressible** in standard TLA+.
- **Gap:** no non-vacuity gate for TLA+ invariants, mirroring the Rego vacuity problem. Same shape
  as floor fitness, one layer down.

---

## 8. ADR log — status as of 2026.09.15

| # | Title | Status |
|---|---|---|
| 0001 | Rename CI domain to `Build` | **Accepted** 09.12 |
| 0002 | Apply `Contain` in Build as well | **Accepted** 09.12 · amendment drafted 09.15 (gate, evictability test) |
| 0003 | Topic per principal per epoch/round | **Accepted** 09.11 · bundling check run 09.15, clauses annotated |
| 0004 | Separate control-plane facts from cognitive payloads | **Accepted** 09.12 · rationale unrecorded |
| 0005 | Kafka is neither ordering authority nor system of record | Held · Observer-gate question |
| 0006 | Erasure is a modeled event | **Accepted** · debt to 0013 · scope is a data class · **confirmation required** (0029 C1) |
| 0007 | Semantic judgment is never a lift | **Accepted** · gates extended to floor; rules floor proposed by 0025 |
| 0008 | Observer replicas not colocated with the Thinker | **Accepted** · **reversed in effect** by 0023 · supersession required |
| 0009 | Break-glass is modeled, quorum-witnessed | **Accepted** · debt to 0013 · TTL missing (B-register) · **confirmation required** (0029 C1) |
| 0010 | Verified object = mechanism + minimal policy floor | **Accepted** · amendment drafted 09.15 (rules floor, change direction) |
| 0011 | Observer placement / fault-domain independence | **Tombstone** |
| 0012 | Default-deny bundle is the policy floor | **Accepted** |
| 0013 | Exception mechanism for privileged paths | **Draft skeleton** · owner Scott · decomposed 09.15 · post-bootstrap |
| 0014 | Floor authorship and change control | **Open** · narrowed to proposal eligibility |
| 0015 | Boundary effects audit | Proposed · revised 09.15 (authority-change set) |
| 0016 | Persona | **Accepted** 09.12 |
| 0017 | Archetype admits only in-house pre-trained Personas | **Accepted** 09.12 · lineage criterion outstanding · ordering-primacy clause reversed in effect by 0023 |
| 0018 | Typed lift splits: decoder in Persona, validator in mechanism | **Accepted** 09.12 |
| 0019 | Optional decode observability | **Accepted** 09.12, narrow form |
| 0020 | Replay scope is boundary events only | **Accepted** 09.12 |
| 0021 | Build effect stream | Proposed · blocked on 0022 |
| 0022 | Build action alphabet | Proposed · revised 09.15 (`Vote`) · §6 confinement undischarged |
| 0023 | Degeneracy as the deployment-variation relation | Proposed · type-change check and versioning needed |
| 0024 | Promotion requires a unanimous quorum | Proposed rev. 4 · 09.15 · reads quorum parameters from rules |
| 0025 | Trust anchor is a havoc issuer; intent is the sole axiom | Proposed rev. 3 · 09.15 · decomposed |
| 0026 | The rules floor bounds every anchor issuance | Proposed rev. 2 · 09.15 · non-vacuity run: R1–R3 parametric, **R4 withdrawn** |
| 0027 | Genesis rules are resident | Proposed · 09.15 |
| 0028 | Forensic floor: authority facts survive erasure and break-glass | Proposed · 09.15 · post-bootstrap |
| 0029 | The design process is genesis; the custodian may ratify unilaterally; the anchor bootstraps on a drafted TLA+ spec | **Accepted (genesis)** 09.15 |

**Unnumbered, pending**
- Observer scoping supersession (per-principal + correlator)
- 0017 ordering-clause supersession
- Provenance, legibility, and Observer-scoping declaration records
- Weakest-link provenance rule

**Count:** 16 accepted (2 confirmation-required), 1 tombstone, 1 held, 9 proposed, 1 draft skeleton (0013), 1 open (0014).
- Two accepted records are reversed in effect.
- Two accepted records carry drafted amendments.

---

## 9. Open list

**Highest risk**

- **ADR-0013.** Owned (Scott), decomposed, back to its 09.12 scope:
  - one grant-authorization model;
  - exception entries and the R6 bound;
  - NC-1 and NC-2;
  - demand type 5.

  The rest has moved:
  - forensic floor → 0028;
  - degeneracy composition → 0023;
  - break-glass TTL → 0026 R8 (candidate);
  - break-glass × promotion and break-glass × issuance → 0026 R7.

  Ratified post-bootstrap under recusal, which answers the independent-reviewer question
  structurally.
- **Bootstrap specification.** Five modules and their non-vacuity mutations (0029 §3). This is now
  the gate on everything post-genesis.
- **Sandbox gap.** Blocks 0022 §6 and 0015's exhaustiveness. It also decides whether `Contained`
  has any members. There is still no mechanism and no owner.

**Decisions**

- **Observer.** Quarantine gate as a modeled event or an internal step (unblocks 0005). Scoping
  supersession of 0008. Veto-seat liveness heartbeat (0024).
- **Floor fitness**, the fourth gate (MEASURE 2.13). Plus a TLA+ invariant non-vacuity gate, same
  shape.
- **Global vs per-class floor**, now for both the policy floor and the rules floor. 0022 is
  evidence for per-class.
- **0017 independent-lineage criterion.**
- **Raw-emission retention**, between 0003 and 0006.
- **Replay authorization vs replay scope.** Clause 0003.5 overlaps ADR-0020; neither says which governs.
- **Non-vacuity check on rules floor R1–R6** (ADR-0026). Blocks ratification.
- **Subtractive promotion fast path** (0024, deferred).

**Declarations**

- **Clock model** — known answer, unwritten.
- **Assumptions of use** — to the front.
- **Liveness assumptions about humans:** weak fairness on `Vote`; anchor custody.
- **Custody row for the ADR corpus:** (1, 0), solo authorship.
- **Monoculture:** cross-family Observer.
- **`L`** as a deployment obligation in the rung tuple; MEASURE 1.1 non-measurement declaration.
- **MANAGE 1.4 residual-risk statement.** Now headed by anchor capture at the capture threshold.
- **`D`** as human-response budget.
- **Owner column and per-boundary adversary** for the boundary register.

**Work items**

- Diagram (two: Build and Run, or one with explicit acknowledgment).
- Component × domain mapping table.
- Signed message format (protobuf vs canonical CBOR). **Genesis-blocking:** the genesis bundle needs it (0029).
- Recruit anchor key-holders and grant seats (≥ 5 humans at the archetype), or declare a degenerate bootstrap custody.
- Vector clock or per-principal sequence number (contingent on the Observer gate).
- Genesis and key ceremony; re-genesis migration.
- **Regenerate the glossary** against this checkpoint.
- Recovered from the 09.10 session:
  - "army of one" degraded mode (GOVERN 6.2);
  - per-component cost table (MAP 3.2);
  - hierarchy-of-needs drop order (MANAGE 2.1);
  - control-plane cost model.

**Publication-blocking sweep — run 09.15**

| Item | Result |
|---|---|
| CI → `Build` rename | **Closed.** Glossary 09.11 already uses `Build`; the Project article copy has no occurrences. The 09.10 checkpoint is history and is not rewritten. |
| Varshney spelling | **Closed** for available artifacts; check any off-Project draft. |
| §4.2 → §4.6 and Appendix B | **Errata drafted** (0007, 0010). The 09.15 records cite correctly. |
| 0022 references | **Errata drafted.** |
| Evictability wording | **Done** in the feature list (P4, F4.2). The glossary needs regeneration, not a sweep (below). |
| Feature list filename and count | **Done.** Renamed to 09.15; count is 48. |
| Delta inventory tally | **Recorded** here (§7.2); the inventory file is not on disk. |
| SLSA citation for 0017 | **Erratum drafted.** |
| **New: ADR-0006 mechanism misstated** | **Corrected** in the feature list and this checkpoint. The external assessment, delta inventory, and feature list said 0006 "crypto-shreds." ADR-0003 rejected crypto-shredding as the primary mechanism; erasure is sealed round-topic deletion plus ADR-0004 plaintext-store deletion. The MANAGE 2.4 contradiction still holds on the correct mechanism. |
| **New: glossary is stale** | The 09.11 glossary predates the 09.12 and 09.15 checkpoints. Entries are now wrong: 0002 unratified, bundle as parameter, deployment ladder, `D` as detection lag. Missing terms include Persona, degeneracy, trust anchor, rules floor, `Contained`/`Mediated`, legibility, and boundary-enforceable containment. **Regenerate against 09.15** — work item. |

---

## 10. Genesis plan: middle path (ADR-0029 revision 2)

**The design process stays in genesis.** The custodian may ratify any record that has decision text,
unilaterally and at any time. Debts go on the record's face. Records touching privileged paths,
exhaustiveness or confinement claims, supersessions, or debt resolution are marked **confirmation
required**. They must pass a confirmation promotion under recusal as the first post-bootstrap work.

The bootstrap set (0024–0027) cannot be confirmation-required. Confirming the rules that confirmation
itself runs under would be circular; the genesis attestation covers those records instead.

**This checkpoint ratifies nothing.** Ratification is a separate act by the custodian. The corpus
manifest v1 lists every record's readiness.

| Class | Records |
|---|---|
| **Ratified** | **0029** (09.15) |
| **Ratifiable now** (decision text exists) | 0024 · 0025 · 0026 (R1–R3, R5, R7) · 0027 · 0028 · 0015 · 0021 · 0022 (all sections) · 0005 · amendments 0002 A1/A2 and 0010 A1/A2 · errata · 0003 annotation |
| **Would be confirmation-required on ratification** | 0028 · 0015 · 0022 §6 · retroactively 0006 and 0009 |
| **Not ratifiable yet** (no decision text) | 0013 (NC-1, NC-2, type 5) · 0014 · 0023 carried scope · Observer bundle · 0008 and 0017 supersessions · weakest-link provenance · declaration records · R6 and R8 |
| **Bootstrap trigger** | Drafted TLA+ bootstrap spec: five modules, five invariants, mutations. *May*, not *must*. |

### Genesis debt ledger

| Measure | Now |
|---|---|
| Confirmation-required records ratified | **2** (0006, 0009: retroactive on 0029) |
| Confirmation-required on ratification of the ready set | **+3** (0028, 0015, 0022 §6) |
| Confirmation-required when written | 0013 and both supersessions (**+3**) |
| Bootstrap specification | **Not drafted** |
| Forcing function | **None**, by decision (0029 §7) |

---

## 11. Next four, in order

**Done this revision**
- **ADR-0029 ratified.** Genesis status classes are live; 0006 and 0009 are marked
  confirmation-required.
- **Rules-floor non-vacuity check run** (`RulesFloorNV.tla`, TLC). Details in ADR-0026 §6. Results:
  - R5 and R7 are non-vacuous.
  - R1–R3 were **vacuous against 0024 as written**: its snippet hard-coded the quorum. 0024 is fixed
    to read `quorum`, `minGrant`, and `recuse` from issued rules.
  - R4 is withdrawn as vacuous in any sensible design; timeout-never-grants is now a 0024 mechanism
    constant.
  - R2's mutation reproduced the vacuous-roster failure: **promotion with zero votes**.

**Next**
1. ~~Re-run the check against 0024 revision 4's exact snippet~~ **Done.** All five entries are
   non-vacuous, promotion is reachable, and all properties hold. Timeout-never-grants holds with an
   empty floor.
2. **Ratify from the ready set** as you choose: 0025, 0026, 0027, 0024, amendments, errata.
3. **Write decision text for 0013** (NC-1, NC-2, demand type 5).
4. **Grow `RulesFloorNV` into the bootstrap modules** (0029 §5). About half of `RulesFloor` and
   `Promotion` already exists.
