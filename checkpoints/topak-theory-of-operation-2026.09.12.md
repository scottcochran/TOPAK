<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: Theory of Operations checkpoint from ADR review session 09.12 (https://claude.ai/chat/07876ffb-88f6-4f95-b7db-6011f705617e), `create_file` turn 1, file `topak-theory-of-operation-2026.09.12.md`. No later edits.
>
> **Superseded** by 2026.09.15 revision 4. Known defects, corrected downstream and not here: the Moon & Varshney §4.2 citations (correct: §4.6 and Appendix B); ADR-0002 A1's struck phrase lives in §1 of this checkpoint, not in the record (Batch A §3).
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

# TOPAK — Theory of Operation

**Checkpoint 2026.09.12** · supersedes 2026.09.11 · *The Gripping Hand*

Previous checkpoint: "Theory of Operation checkpoint with ADR references" (2026.09.11). This
one is built on the **ADR review session of 2026.09.12**, in which nine Architecture Decision
Records (ADRs) were ratified, one was tombstoned, three new ones were opened, and the
verification-locus question produced a structural result that reorganizes several other
decisions around it.

Supporting sessions since 09.11: the HITL/HOTL terminology pass, the principal-roles pass,
the human-as-LTRO session, the glossary, the compose-rig and minimum-model sessions.

---

## 0. The ledger

| 2026.09.11 | 2026.09.12 |
|---|---|
| `Build(Contain) → Run(Contain)` proposed, decision required | **Accepted** (ADR-0002). `Contain` is a component instantiated twice, not a third domain. |
| Verified object = mechanism, bundle = parameter | **Amended and accepted** (ADR-0010). A **minimal policy floor** is verified with the mechanism; operational bundles are parameters admissible only if they refine it. |
| Default-deny bundle is pre-blessed and resident | **Accepted and promoted** (ADR-0012). It *is* the floor — same artifact, new proof obligation. |
| Erasure and break-glass as modeled events | **Accepted with debts** (ADR-0006, ADR-0009). Both are now floor exceptions, ratified against an unwritten ADR-0013. |
| Ten ADRs, one Accepted | Ten ratified, one tombstoned, three open (0013, 0014, 0015), two pending (0004 text, 0005). |
| Human oversight described informally | Formalized by enabling condition; principal-vs-gate settled on evictability. |
| Principals are agent LTROs | **Widened.** Principal type is universal; effect exclusivity demotes to a per-principal predicate. |

---

## 1. Domain symmetry closed

**ADR-0002 accepted.** `Build(Contain) → Run(Contain)`. The fork was dissolved rather than
decided: the two candidate answers described different things in Build. Agents drafting specs
and Rego inside Build are under mechanism enforcement (`Contain`); the *promotion* gate above
them is a human signing key. Option 1 and Option 2 were never exclusive.

The clean test that produced it, from the principal-roles session: **if you can be evicted,
you are a principal; if you are the authority that evicts, you are at the gate.** `Contain` is
parametric in its occupant, so the occupant is by definition replaceable. A gate approver is
not, which is exactly why they sit outside.

What comes with it:

- The trusting-trust regress terminates at a declared axiom set plus — after ADR-0010 — one
  verified artifact, rather than by declaration alone. See §2.
- The proof surface doubles, and **Moon & Varshney §4.2 is now a threat inside Build**, since
  a human signing a green pipeline is precisely the failure they documented. This promotes
  ADR-0007's totality checks from work item to **required Build gate**.
- `Contain` listed once and instantiated twice means the article's two axes are components ×
  domains with one component appearing in both domains. The mapping table is still unwritten
  and this makes it more necessary, not less.

**New open item.** Build's membrane has no effect stream. ADR-0003's round-topic scheme is the
unit of erasure in Run; Build's unit is an artifact, not a round. Either Build's `Contain`
emits to round-topics too — inheriting broker metadata pressure in the pipeline — or Build's
containment has a different observability substrate. Smaller than the asymmetry just closed,
but real and currently unstated.

---

## 2. The minimal policy floor — the session's structural result

**ADR-0010, as ratified:** the verified object is the enforcement mechanism, its version
pinning, its epoch fencing, and a **minimal policy floor**. Operational bundles remain
versioned parameters, admissible only if they refine the floor — they may subtract authority,
never add it. Refinement (`bundle ⊑ floor`) is decided at promotion time as a Build
obligation. **One floor, shared by Build and Run**, instantiated through the same `Contain`
component per ADR-0002.

### Why neither pure option was right

**Pure parameter** gives a universally quantified but *relative* result: for all bundles B, the
mechanism enforces B faithfully under epoch discipline. Every safety property is conditional
on B, and `B = allow-all` satisfies it perfectly. Containment becomes *enforcement fidelity ∧
bundle adequacy*, with the second conjunct discharged by Build gates rather than by proof.

**Pure inclusion** gives an absolute result about a concrete B — no agent reaches a forbidden
state, full stop, which is what Theorem 3.2 buys. The price: the theorem is only about that B,
every policy edit invalidates it, the state space scales with policy complexity, and the rate
mismatch is severe (mechanism changes at release cadence, policy at incident cadence).

**The rebuttal to Moon & Varshney, on their own ground.** Inclusion does not eliminate the risk
of a bad policy; it relocates policy correctness from a runtime-gated path to a Build-gated
one. TOPAK's published inversion is that the Byzantine threat *lives in Build*, and §4.2's
failure — a vacuously true predicate sailing through green gates — was a Build failure. So
inclusion moves the thing you care about into the domain TOPAK declares hostile. This belongs
in ADR-0010's rationale as stated, not discovered.

### What the floor buys

- **Containment properties are proven absolutely** against the floor and cannot be weakened by
  any admissible parameter.
- **Stale bundles become monotone-safe** — bounded below by the floor regardless of age. EL
  zone 1 survives intact, sound *by construction* rather than by operational care. Same shape
  as the lease argument: expiry is a local clock read, expired is safe.
- **The refinement check lands in Build**, where unavailability costs a stalled pipeline and
  nothing more. ADR-0007's syntactic-lift discipline guarantees a finite, totally-extracted
  action alphabet, which makes `bundle ⊑ floor` decidable rather than aspirational —
  exhaustively or by SMT at Build time.
- **Build's recursion gets a terminating base case on a verified artifact** rather than a
  declared axiom set. The floor is the one artifact verified rather than promoted. A
  Build-domain escape and a Run-domain escape collapse into one proof obligation.

### What it costs

- **The floor must stay minimal.** Its reviewability by a human at deploy cadence is the entire
  basis for trusting Build's HITL gate. Pushing operational policy into it for availability
  reasons destroys that and re-couples policy to release cadence. Resist on those grounds,
  not on size.
- **Floor changes are genuinely expensive** — deploy-cadence, consensus-ordered. Right price,
  needs stating.
- **A vacuous floor admits every bundle** and discharges every containment property over
  nothing, invisibly. This is the widest-blast-radius silent failure in the system, which is
  why ADR-0007's totality, non-vacuity and discrimination gates now run **on the floor itself**,
  not only on operational bundles. That extension is the only thing standing between TOPAK and
  its own §4.2.

**Unresolved:** one global floor, or one per principal class. Global is provable and may be too
restrictive to be useful; per-class multiplies refinement checks. Not blocking, but it shapes
ADR-0014.

---

## 3. Monotonicity, now at three levels

The same principle appears three times, and this is the sharpest through-line the design has:

| Layer | Statement | Status |
|---|---|---|
| Decision | Consensus for grants, local for denials | Established |
| Policy | Operational bundles may only subtract relative to the floor | ADR-0010, accepted |
| Deployment | Lower rungs are documented subtractions from an archetype | Pending — axis question unresolved |

The argument is identical at each level: a wrong denial costs availability, a wrong grant costs
containment. Worth naming as a single principle in the article rather than restating it three
times in three vocabularies.

---

## 4. Human oversight, formalized

From the HITL/HOTL sessions. Define the terms in TOPAK's own primitives — by what the loop does
when the human does not act — rather than importing the autonomy-doctrine debate:

- **HITL** (human-in-the-loop) — human action is an *enabling* condition of the transition. No
  act, no progress.
- **HOTL** (human-on-the-loop) — human action is never enabling, only *disabling*. Progress
  continues; intervention subtracts.
- **HOOTL** (human-out-of-the-loop) — no channel exists. Not "nobody acted" but "no action was
  expressible."

All three are then model-checkable in TLA+, and HOTL falls straight out of
consensus-for-grants/local-for-denials: an on-the-loop human can only ever deny.

**The placement of humans is forced, not chosen.** Build is PC/EC — unavailability costs a
stalled pipeline, so the loop can afford to block, so HITL is affordable. Run carries
`W < L < D` with a ~1s propagation window — no human fits inside it, so HITL is *unavailable*,
leaving HOTL. Derive it that way in the article instead of asserting it.

Three corrections that came out of the same pass:

- **Admins are not purely HOTL.** Erasure (0006) and break-glass (0009) are grants, and grants
  need consensus. Write it as *HOTL by default, HITL at break-glass and erasure,
  quorum-witnessed in both.* Filing admins as flat HOTL makes every non-denial admin action an
  unmodeled effect path — effect-exclusivity collapse with a human in it.
- **HOTL without a response budget is decoration.** An admin who *may* intervene but is never
  required to is structurally the ignored first-officer warning. `D` in `W < L < D` is a
  human-response budget, not just detection lag.
- **HITL reappears in Run** wherever ADR-0007's reversibility index moves the guarded unit from
  action to stage. Quarantine release is a HITL gate.

**E-stops versus break-glass.** E-stops are unilateral and authority-subtracting; break-glass is
quorum-witnessed and authority-granting. Lease expiry is a *passive* e-stop requiring no human
action at all. Through-line across domains: human authority moves from constitutive (Build) to
supervisory (Run) to absent (Contain), while enforcement shifts from judgment to consensus to
mechanism.

Scope correction on `Contain`: its "hard rule enforcement" claim covers **syntactic envelope
enforcement only**. Semantic concerns are Observer detection, not enforcement.

---

## 5. Principals: `Contained` versus `Mediated`

From the human-as-LTRO session. Wrapping human users in `Run` as principals falls straight out
of `Run(Contain)` — the membrane is parametric in its occupant and a human behind a console
harness satisfies the action alphabet. But wrapping changes the **type, not the assumption**:
effect exclusivity is false for humans by construction. The phone call is still there.

**The move is to split the two.** Make the principal type universal — identity, lease, typed
alphabet, topic, epoch, eviction — and demote effect exclusivity from a global assumption to a
per-principal predicate:

- **`Contained(p)`** — effect exclusivity claimed. Safety properties ("no forbidden state is
  reached") quantify here only.
- **`Mediated(p)`** — in-band actions typed and policed, out-of-band effects possible.
  Attribution and authorization properties ("every exercise of authority traces to a
  lease-holding principal at a known epoch") hold here too.

Humans are `Mediated`, never `Contained`. A TLA+ predicate on the principal set rather than a
structural claim baked into the domain, and it says precisely which theorems survive the
widening.

**The strongest reason to take it:** human grants stop being privileged. Today an approver's
sign-off is a distinguished trusted action, which means a coerced or compromised operator holds
more authority than a Byzantine agent. As an LTRO, their approval is a grant, and grants need
consensus. The semantic-lift rule generalizes without modification — a human's "this looks
wrong" is an Observer finding, admissible as a deny or quarantine trigger, inadmissible as an
admit precondition.

Three edges:

- **E-stop does not deadlock** under an expired lease or fenced epoch. Stop power is exercised
  by *not* refreshing the deadman, which requires no authority. State it, because readers will
  assume otherwise.
- **Human principals are atomic.** Devs and users do not decompose into Listener/Thinker/
  Reader/Observer, so a human principal has **no internal separation of duties** while an agent
  principal has four. The human occupant is the *less* contained one. Uncomfortable; state it
  outright rather than let a reviewer find it.
- **It makes the sandbox gap undeniable.** TOPAK has a containment *claim* and no containment
  *mechanism*. Humans are the case where that cannot be papered over — which is probably useful.

---

## 6. Privileged paths and the composition hole

Erasure (ADR-0006) and break-glass (ADR-0009) are both ratified, and both are now **floor
exceptions** rather than ordinary refining bundles — erasure is privileged, break-glass *adds*
authority, and neither can be expressed as a subtraction. They are verified-object exceptions
changing at deploy cadence.

Both are ratified against **ADR-0013, which does not exist.** That is the highest-risk item on
the board. Its obligations:

- One authorization model for both, not two predicates arrived at separately.
- **Non-composition** — break-glass chained with erasure must not yield an untraceable bypass.
  The sharpest property in the set, and currently nobody's proof obligation.
- A bound on exception count, so the floor does not lose reviewability by accretion.
- Resolution of **demand type 5** (hide that a record ever existed), now entangled with
  break-glass: a privileged path that can suppress an erasure record either closes type 5 by an
  ugly route or opens a hole, and which one cannot be determined until 0013 exists.

Standing tension: each exception is a carve-out against ADR-0010's minimality requirement, and
minimality is what makes the Build HITL gate trustworthy. Two carve-outs is the current count.

---

## 7. ADR log — status as of 2026.09.12

| # | Title | Status |
|---|---|---|
| 0001 | Rename CI domain to `Build`; adopt `Build(Contain) → Run(Contain)` | **Accepted** 09.12 (text amended per 0002) |
| 0002 | Apply `Contain` in Build as well | **Accepted** 09.12 |
| 0003 | Topic per principal per epoch/round, sealed on emit completion | **Accepted** 09.11 — bundling check outstanding |
| 0004 | Separate control-plane facts from cognitive payloads | **Accepted** 09.12 |
| 0005 | Kafka is neither ordering authority nor system of record | Held with deployment profiles; clean against the archetype, pending the Observer-gate question |
| 0006 | Erasure is a modeled event | **Accepted** 09.12 — debt against 0013 |
| 0007 | Semantic judgment is never a lift | **Accepted** 09.12 — totality gates extended to the floor |
| 0008 | Observer replicas are not colocated with the Thinker | **Accepted** 09.12, whole |
| 0009 | Break-glass is a modeled, quorum-witnessed path | **Accepted** 09.12 — debt against 0013 |
| 0010 | Verified object = enforcement mechanism + minimal policy floor | **Accepted** 09.12 |
| 0011 | Observer placement / fault-domain independence | **Tombstone** — superseded by 0008 before assignment; no decision content |
| 0012 | Default-deny bundle is the policy floor: pre-blessed, resident, verified | **Accepted** 09.12, amended same day |
| 0013 | Exception mechanism for privileged paths through the floor | **Open**, owner required |
| 0014 | Floor authorship and change control | **Open** |
| 0015 | Boundary effects audit | **Proposed** (drafted) |

**Note to add to 0008:** the orchestrator-level Observer scoping — shared replicated group
rather than per-agent, carrying the ~9 vs ~40 instance argument — is ratified as part of this
record, not merely a consequence of placement. A future revisit of per-agent Observers amends
an ADR whose title is about colocation.

**Note to add to 0012:** it was ratified ahead of its parent (0010) on an independent
availability argument — fail-closed must work under partition and at cold start, which rules
out any bundle-fetch dependency. That argument stands regardless of where verification locus
landed. 0010 subsequently made the resident bundle the verified floor: a promotion in status,
not a change of mechanism.

**0011 tombstone text:** "Proposed as a split of ADR-0008 (Observer placement and fault-domain
independence); superseded before assignment when 0008 was accepted whole. No decision content.
See ADR-0008." No renumbering — gaps in an ADR log are self-documenting; silent renumbering is
what breaks cross-references.

**Decomposition test, for reuse:** can a clause be superseded on its own? If a future change
flips one part and leaves the rest standing, it was a separate decision. 0008 and 0010 were
both tested this way; 0010 split, 0008 was taken whole with the consequence noted. **0003 has
not been tested** — it bundles topic granularity, ACL model, retention scoping, replay
authorization, wrapper-Rego masking, and no-tiered-storage. The masking clause looks
independently supersedable.

---

## 8. Open list

**Decisions**

- **ADR-0013** — exception mechanism. Non-composition is nobody's proof obligation and both
  instances are already ratified. Highest risk on the board.
- **ADR-0014** — floor authorship and change control. "Who may propose a floor change" is a
  different authorization question from "who may promote a bundle," and it is where the human
  key and the vacuity gates concentrate.
- **ADR-0015** — boundary effects audit. Drafted, needs ratification.
- **Global floor versus per principal class.** Shapes 0014.
- **Observer quarantine gate — modeled event or internal step?** Cheapest open question, and it
  unblocks 0005 and may remove the vector clock from this list entirely.
- **Deployment profiles.** Archetype as design target, lower rungs as documented subtractions.
  Axis question unresolved.
- **ADR-0003 bundling check.**

**Work items, carried from 09.11 and still unaddressed**

- The **diagram**. Has a spine (`Build(Contain) → Run(Contain)`) and required content (the
  1→2→3 assumption chain). Still not drawn.
- **Component × domain mapping table.** More necessary after 0002, not less.
- **Signed message format** — protobuf versus canonical CBOR.
- **Vector clock and causal-frame design**, contingent on the Observer-gate answer.

**New this cycle**

- Build's membrane has **no effect stream** (§1).
- `Contained` / `Mediated` predicate needs writing into the spec, and the theorem inventory
  needs splitting to match (§5).
- **Human-response budget** as `D` in `W < L < D`, rather than detection lag alone (§4).
- **CI → `Build` rename sweep** across the 09.10 checkpoint, the glossary, and the draft
  article. Trivial, and the one that most directly hurts publication if missed.
- Monoculture declaration in the rung manifest — one model family across LTRO seats is a shared
  blind spot, cross-family Observer required.

---

## 9. Next four, in order

1. **Observer quarantine gate.** Cheapest, unblocks 0005, possibly deletes a vector-clock work
   item.
2. **ADR-0013.** Both instances ratified; the composition hole is the highest-risk item here.
3. **CI → `Build` rename sweep.** Trivial and publication-blocking.
4. **ADR-0003 bundling check.** Masking looks independently supersedable.
