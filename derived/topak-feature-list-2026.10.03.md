# TOPAK — Feature List

**2026.10.03** · derived · drawn from Genesis Checkpoint G9 (2026.10.02), Theory of Operation revision 13 and the
record files at the tree after `0f94f31` · regenerates `topak-feature-list-2026.09.15.md`, which it supersedes as
basis · Playbook marks are `topak-playbook-delta-inventory-2026.10.03.md`'s · prepared by Claude at the custodian's
request

A feature list derived from the state of record, grouped by the eight organizing principles the 09.15 list proposed,
with each feature's basis in a record or a narrative section, its status at G9, and its correspondence to the NIST AI
RMF Playbook. The 09.15 list was drawn from a checkpoint with fourteen records; this one is drawn from forty-five.

**Basis and limits.**

- Features come from G9 and the records it ratifies. A pending amendment (ADR-0034 A2, ADR-0033 A7, A8; ADR-0023 A1
  and ADR-0034 A3 drafted 2026.10.03) is listed as **Pending** and counts for nothing. What the reference builds under
  a pending text is listed as **Built**, which is evidence and not a record (ADR-0033 §1).
- The eight principles are still a synthesis, not a ratified list. The 09.15 list asked that they be ratified or
  rejected before appearing in an article; nothing has. Two have changed meaning: P1 now has proofs behind it, and P7
  now has a failure direction (ADR-0039).
- A **confirmation-required** record is ratified by one person and awaits the first post-bootstrap quorum (ADR-0029
  §4). Its features are listed as Accepted and are to be cited as author-ratified (ToO §0, A8).

**Status key**

| Status | Meaning |
|---|---|
| **Accepted** | Ratified record, genesis phase; a `C` marks a confirmation-required criterion |
| **Proposed** | A record or section drafted and not ratified (ADR-0005, 0035, 0036; ADR-0042 §6) |
| **Pending** | An amendment to an accepted record, marked inline and not applied |
| **Built** | Exists at the reference under a pending or proposed text; cited by no record in force |
| **Proved** | A TLA+ invariant proved by TLAPS (ADR-0046) and checked by TLC; of the module, not the code |
| **Open** | Named on G9's open list; no decision |

**Playbook mark key:** M matched · P partial · C convertible · G gap · X out of scope, as the inventory defines them.

---

## The eight principles

| # | Principle | One-line statement at G9 |
|---|---|---|
| **P1** | Verify the cage, not the occupant | Containment is stated about the mechanism under havoc semantics and proved of its modules; the model is untrusted by assumption; what runs is shown to agree with the model on tested paths |
| **P2** | Monotone authority, fail closed | Authority changes only by promotion or issuance; grants need consensus, subtractions do not; bundles and renewals only subtract; every failure lands on deny or stall |
| **P3** | One containment component, two domains | `Build(Contain) → Run(Contain)`; each domain has its own typed alphabet and shares only the carrier |
| **P4** | Universal, evictable principals | One principal type for agents and humans, one seat each; a principal is anything evictable by an authority other than itself |
| **P5** | Oversight placed by consistency budget | HITL, HOTL and HOOTL follow from each domain's budget `W + L + D < T_irrev`; the budget is a form with its numbers undeclared |
| **P6** | Privileged paths are modeled events | Erasure, break-glass, revocation and the fence are transitions in the specification with properties and mutations |
| **P7** | Independent observation, bounded evidence | Detection is per cell, placed off the Thinker's fault domain, coupled to admission so that absence stalls; collusion is the declared gap |
| **P8** | Recorded, decomposable, self-measuring decisions | Every fork is a record with typed history; every cut is measured by a manifest that verifies at its commit; drift between records, modules, proofs and code is caught by tooling |

---

## 1. P1 — Verify the cage, not the occupant

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F1.1 | **Havoc semantics.** Agents are unverifiable in principle; every guarantee is stated against what the action alphabet allows. Concordant with Moon & Varshney Theorem 3.2 | ToO §2.1, §2.3 | Accepted (ADR-0007, 0010) | MAP 2.2 P · MEASURE 2.9 X (declared) |
| F1.2 | **The verified object** is the mechanism, its epoch discipline and a minimal policy floor; bundles are parameters | ADR-0010 | Accepted | MAP 4.2 M |
| F1.3 | **Typed action alphabets**, Build (`Read`, `Draft`, `Emit`, `Submit`, `Invoke`, `Vote`) and Run (`Consult`, `Actuate`, `Report`); semantic judgment is never a lift | ADR-0007, 0022, 0040 | Accepted (0040: C3, C4) | MAP 3.3 M |
| F1.4 | **The floor gates**: totality, non-vacuity, discrimination, entry-matters and routing, run on the floor itself; routing's `holds` counts only with a checked proof | ADR-0030 §5, A1 | Accepted (C1) | MEASURE 2.1 M · MEASURE 2.13 G (the fourth gate) |
| F1.5 | **Composition**: `admit ⟺ floor_permit ∧ ¬bundle_deny`; an engine error is a deny; a bundle cannot write a floor input | ADR-0030 §1, §4 | Accepted (C1); Proved (`FloorComposition_proof`) | MANAGE 2.3 M |
| F1.6 | **Fifteen TLA+ modules, mutation-tested and proved**: every stated invariant holds for every constant the assumptions admit; mutations and witnesses stay with TLC; TLC versus TLAPS declared | ADR-0046; `spec/` | Accepted (C2, C4); 3,036 obligations | MAP 1.6 M · MAP 2.3 M |
| F1.7 | **Trace validation**: every tested behaviour of the reference replayed through an operational model, every state read against the abstract confinement invariants | ADR-0033 A5; `spec/Mechanism.tla`, `ConfinementRefinement.tla` | Accepted (A5); 62 traces at A8 (pending) | MEASURE 2.1 M · MEASURE 2.3 P |
| F1.8 | **The refinement gap is a named row**: no machine-checked chain from modules to code; every theorem is conditional on it for a running deployment | ADR-0045 T-0045-28 | Accepted (C2, C4); the row's closure Open (item 56) | MANAGE 1.4 (input) |
| F1.9 | **Confinement attested at grant**: a promoted profile P1–P7, three verdicts, no silent downgrade at grant or renewal, the session bound to the attested guest | ADR-0034 | Accepted (C2, C4); Proved (`Confinement_proof`, `Confinement_A1_proof`) | MAP 4.2 M |
| F1.10 | **`Contained` as a lookup** naming each failing conjunct; `Mediated` is the rest; rung 0 is never `Contained` | ADR-0034 §4; ADR-0031 §3 | Accepted; Proved (`Rung0NeverContained`) | MANAGE 1.4 (input) |
| F1.11 | **The launcher in the node**: launch, appraise, grant, bridge; rung 1 real on a process or container, rung 3 SIMULATED, rung 2 a seam | ADR-0036 §6; ADR-0033 A7 | Proposed (0036); Pending (A7); Built | MEASURE 2.3 P |
| F1.12 | **A first `Contained` candidate**: a P3-passing image under a declared profile | ADR-0036 §4 | Open (item 36) | — |
| F1.13 | **Run tools held to their channel**: a Run tool as a Wasm module whose only network capability is its declared target; P4 for Run is channel fidelity | ADR-0034 A2; ADR-0033 A8; `RunConfinement.tla` | Pending (A2, A8); Proved (`RunConfinement_proof`); Built | — |
| F1.14 | **The trusted base, row by row**: thirty-one rows, each with class and residual; a component enters only if its failure can only subtract or its identity is issued | ADR-0045 | Accepted (C2, C4) | MAP 4.2 M · GOVERN 4.2 P |
| F1.15 | **The theorem inventory, computed**: which guarantees are void for a declared trusted base | `spec/theorem-premise-binding.md`; `spec/inventory.py` | Draft table; script | GOVERN 1.3 P · MAP 1.5 P |

---

## 2. P2 — Monotone authority, fail closed

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F2.1 | **Authority changes are exactly promotion and anchor issuance**; everything else happens within the rules in force | ADR-0015; ADR-0045 Context | Accepted (C2) | MANAGE 2.4 M |
| F2.2 | **Consensus for grants, local for subtractions**: revocation, abstention and expiry need no quorum and are still ordered | ADR-0031 §5; `mechanism/` finding 3 | Accepted (C1); Proved (`Lease_A1_proof`) | MANAGE 2.4 M |
| F2.3 | **Resident default-deny floor**, pre-blessed and verified; works at cold start and under partition | ADR-0012, 0027 | Accepted | MANAGE 2.3 M |
| F2.4 | **Bundles cannot add authority by construction**; a bundle loads only under a signature that verifies under a key in the issued rules | ADR-0030; ADR-0044 | Accepted (C1) | MANAGE 4.1 P |
| F2.5 | **Renewal only subtracts**: same rung, same bundle, same round and role; a renewal that cannot re-attest lapses | ADR-0031 §4, A1 | Accepted; Proved (`LeaseAuthorityMonotone`) | MANAGE 2.4 M |
| F2.6 | **Lease expiry as passive e-stop**; the epoch fence as the fleet's active one; targeted revocation beside it | ADR-0031 §5 R3; ADR-0032 | Accepted; Proved (`NoActionUnderFencedEpoch`, `RevokedStaysStopped`) | MANAGE 2.4 M (reverse delta) |
| F2.7 | **Degeneracy as the deployment-variation relation**: a rung is a documented subtraction from the archetype; the inventory is theorems minus voided premises; type changes declared | ADR-0023 | Accepted (C3) | GOVERN 1.3 P · MAP 1.5 P |
| F2.8 | **The deployment declaration**, naming the trusted base and, pending, the declared rung per seat | ADR-0045 §1; ADR-0023 A1 | Accepted schema; template Open (item 64); A1 Pending | GOVERN 1.3 P |
| F2.9 | **The apply-time re-check**: an admit decided under one epoch is voided if committed after a fence; the appraisal is re-checked at apply on every replica | ADR-0033 §4; ADR-0034 §3.2 | Accepted | MANAGE 2.3 M |

---

## 3. P3 — One containment component, two domains

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F3.1 | **`Build(Contain) → Run(Contain)`**: one component instantiated twice; Build is where the Byzantine threat lives | ADR-0001, 0002 | Accepted | MAP 4.2 M (reverse delta) |
| F3.2 | **Run has its own alphabet** and shares only the carrier with Build; no name crosses domains | ADR-0040 | Accepted (C3, C4); Proved (`NoNameCrossesDomains`) | MAP 3.3 M |
| F3.3 | **Run's policy obligations**: one envelope per variant; coupling on effects only; `Consult` never coupled | ADR-0041 | Accepted (C1, C4); Proved (`ConsultNeverCoupled`) | MANAGE 2.3 M |
| F3.4 | **Run's mechanism obligations**: the sequence counts effects, every `Actuate` leaves a record with both digests, the round seals when the lease ends | ADR-0042 §1–§5 | Accepted (C4); Proved (`SealCountsEffects`, `RoundBoundCountsAll`) | MANAGE 4.3 P (the inference receipt, TACIP 10.1.2) |
| F3.5 | **Run's confinement**: channel fidelity with an owner, the tool host's Wasm runtime | ADR-0042 §6; ADR-0034 A2 | Proposed (§6); Pending (A2); Built | — |
| F3.6 | **Build's effect stream and Build Observer** | ADR-0021 | Accepted (C4) | MEASURE 2.4 P |
| F3.7 | **Trusting-trust regress terminates** on the verified object plus a declared axiom set; the toolchain and prover are rows | ADR-0010; ADR-0045 T-0045-29 to 31 | Accepted | GOVERN 4.2 P |

---

## 4. P4 — Universal, evictable principals

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F4.1 | **The lease is the composite credential**: twelve closed fields, one live lease per seat, granted by consensus at a fresh fence | ADR-0031 | Accepted (C1; C2 for A1) | GOVERN 1.6 P (a live inventory of principals) |
| F4.2 | **Evictability test**: a principal is anything evictable by an authority other than itself; whatever is not is at the gate | ADR-0002; ToO §7.5 | Accepted | GOVERN 3.2 M |
| F4.3 | **Seats, cells, stages**: Thinker and Observer are seats, Listener and Reader are stages, a principal holds one seat; only Thinkers author or actuate | ADR-0037, 0043 | Accepted (C3, C4; C4); Proved (`OneSeatPerPrincipal`, `OnlyThinkersAuthor`, `OnlyThinkersActuate`) | GOVERN 2.1 M |
| F4.4 | **Attribution**: every exercise of authority traces to a lease-holding principal at a known epoch; holds for `Mediated` principals too | ADR-0031; ADR-0028 F2 | Accepted | MEASURE 2.8 M |
| F4.5 | **Human grants are unprivileged**: approval is a grant needing consensus; a human finding may deny and never admit | ADR-0007; ToO §2.3 | Accepted | GOVERN 3.2 M |
| F4.6 | **The Persona**: the model enters as a pinned artifact (weights, prompt, decoder), attested at grant and renewal, re-attested at least every `T_persona` | ADR-0016, 0018, 0031 A2 | Accepted | MANAGE 3.2 P |
| F4.7 | **In-house provenance at the archetype**; lineage as a projection of the Build log; independence as an exclusion rule with thresholds | ADR-0017; ADR-0035 | Accepted (0017); Proposed (0035) | MANAGE 3.1 P |
| F4.8 | **No token enters a launched guest**: at rung 1 the bridge is the session; at rung 3 the attested session key signs every action | ADR-0036 §2; ADR-0034 §3.5 | Proposed (0036); Built (A7 pending) | — (TACIP 13.2.3) |
| F4.9 | **Clean principal decommissioning**: revocation, fence, expiry, break-glass lapse; a revocation is permanent within the chain | ADR-0031 §5 | Accepted | GOVERN 1.7 P |
| F4.10 | **No delegation model**: a principal cannot create a subordinate | — | Open (item 51); undeclared as a position | — (TACIP 13.2.2) |

---

## 5. P5 — Oversight placed by consistency budget

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F5.1 | **HITL, HOTL, HOOTL by enabling condition**: enabling, disabling only, no channel expressible | ToO §2.6 | Derived | GOVERN 3.2 M |
| F5.2 | **The clock model**: clocks buy liveness, never safety; intervals trusted by failure direction; no safety decision reads a principal's clock | ADR-0032 | Accepted | MANAGE 2.3 M |
| F5.3 | **`W + L + D < T_irrev` per effect class** | ADR-0032 §4 | Accepted as a form; `L` unmeasured, `T_irrev` undeclared (residual-risk statement §5) | MAP 3.5 P · MEASURE 3.2 G |
| F5.4 | **Promotion is a unanimous quorum grant** with the author recused, gates enabling the vote, and a veto seat covering to the seal | ADR-0024, A2 | Accepted; Proved (`P1_Unanimity` to `P9_NoSoloGrant`) | MANAGE 1.1 P |
| F5.5 | **Admins are HOTL by default, HITL at break-glass and erasure**, quorum-witnessed | ToO §2.6; ADR-0009, 0006 | Derived | GOVERN 3.2 M |
| F5.6 | **Operator proficiency** | — | Open (MAP 3.4) | MAP 3.4 G |

---

## 6. P6 — Privileged paths are modeled events

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F6.1 | **Erasure as a modeled, consensus-ordered event**; topic per principal per round as the unit of erasure; demand taxonomy | ADR-0006, 0003 | Accepted (C1, C4; C1 for A2); unbuilt at the reference | MEASURE 2.10 C |
| F6.2 | **Break-glass as a modeled, quorum-witnessed path**; exceptions bounded in count (R6) and barred from `Issue`, `Vote` and promotion (R7) | ADR-0009, 0013, 0026 | Accepted (C1, C4); Proved (`P7_BGNoAuthority`, `BreakGlassNeverChangesAuthority`) | MANAGE 2.4 M |
| F6.3 | **Non-composition**: break-glass and erasure cannot compose; only admitted effects go via break-glass | ADR-0013 §4 | Accepted; Proved (`NC1`, `NC2`; the second clause found by the prover) | MANAGE 2.4 M |
| F6.4 | **The forensic floor**: authority facts survive erasure and break-glass; stop attribution is non-erasable | ADR-0028 | Accepted (C1) | MANAGE 2.4 M · GOVERN 1.1 X (no legal-basis line, CR-11) |
| F6.5 | **The rules floor bounds every anchor issuance**: R1, R2, R5, R6, R7, R9 in force; the anchor is a havoc issuer with intent as the sole axiom | ADR-0025, 0026 | Accepted; Proved (`FloorPreserved`, `RulesFloorNV_rev5_proof`) | MANAGE 2.4 M |
| F6.6 | **The break-glass TTL (R8)** | ADR-0026 A1 | Pending, four conditions unmet (item 8) | MANAGE 2.4 (CR-29) |
| F6.7 | **Break-glass under a dead Observer**: R3 couples it | ADR-0039 R4 | Accepted as written; Open (item 49) | MANAGE 2.4 (CR-29) |
| F6.8 | **Denials recorded**: on the round topic under an open round, in the bounded `after` companion after the seal | ADR-0020; ADR-0033 R8; ADR-0003 A2 | Accepted | MANAGE 2.3 M |
| F6.9 | **Floor authorship and change control**: who may propose a floor change; the per-class floor question | ADR-0014 | Reserved, no file | GOVERN 1.5 P |

---

## 7. P7 — Independent observation, bounded evidence

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F7.1 | **Observers per cell**, off the Thinker's fault domain; the shared group becomes the correlator; any-of denies | ADR-0038 | Accepted (C3, C4); Proved (`DenyByAnyOf`, `ReachIsBounded`) | GOVERN 2.1 M · MEASURE 1.3 G (the Observer is a fixture) |
| F7.2 | **Liveness is progress, not presence**: every Run admit coupled to a live Observer's heartbeat and watermark; a dead, partitioned or starved Observer stalls its Thinker | ADR-0039 | Accepted (C4); Proved (`NoAdmitWithoutLiveObserver`, `UnreadBounded`, `UnreadEffectsBounded`) | MEASURE 2.4 P · GOVERN 6.2 P |
| F7.3 | **Collusion is the declared gap**: every liveness fact is the Observer's assertion; lineage independence is the only cover | ADR-0039 §5; ToO A13 | Accepted as declared; cover Proposed (0035) | MEASURE 2.4 P |
| F7.4 | **The correlator never gates** | ADR-0039 §4 | Accepted; Proved (`CorrelatorNeverGates`); its function Open (item 43) | MEASURE 2.4 P |
| F7.5 | **Control-plane facts separated from cognitive payloads**; Kafka is transport, not the ordering authority | ADR-0004, 0005 | Accepted; Proposed (0005) | MEASURE 2.10 C |
| F7.6 | **Replay is boundary events only**; the `consumed` set makes ingress exactly the admitted `Read`s | ADR-0020; ADR-0037 | Accepted | GOVERN 4.3 P · MANAGE 4.3 P |
| F7.7 | **Decode observability**, optional; logprobs can deny and never admit; conformance admits only at rung 3 under a reserved row | ADR-0019; ADR-0037 §3 R3; T-0045-21, 26 | Accepted | MEASURE 2.4 P |
| F7.8 | **The coupling constants** `T_obs`, `K`, `R` as floor values | ADR-0039 §1; `floor/genesis-values.json` | Accepted as placeholders; Open (item 47) | MEASURE 3.2 G |
| F7.9 | **The quarantine hold** (`K = 0`) | ADR-0039 finding 1 | Open (item 48) | MEASURE 2.4 P |

---

## 8. P8 — Recorded, decomposable, self-measuring decisions

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F8.1 | **Forty-five record files**, numbered to 0046, with typed History rows: amendments, errata, revisions, dependent entries; a record is never edited after ratification except by one | `decisions/README.md` | Practice | GOVERN 1.4 M |
| F8.2 | **Genesis**: the custodian ratifies unilaterally under four confirmation criteria; the entire corpus is reviewed at bootstrap; the ledger names the reviewer | ADR-0029, A2 | Accepted; the A2.5 line carried in `checkpoints/README.md` since 2026.10.03 | GOVERN 1.5 P · MEASURE 1.3 G |
| F8.3 | **Checkpoints as the state of record**, one cut each, never revised; a manifest per cut that verifies at its commit; errata recorded in the resolution point | `checkpoints/`; `tools/verify-manifest.sh` | Practice; 21 manifests verify | MANAGE 4.3 P |
| F8.4 | **Drift caught by tooling**: corpus pins fail the reference's build when a cited record moves; proof-sync fails when a module moves under its proof or a results file cites another prover; check-refs fails on a dead citation | `mechanism/corpus-pins.sha256`; `spec/proof-sync.sh`; `tools/check-refs.py` | Practice | MANAGE 4.3 P |
| F8.5 | **Every tool a result rests on is pinned**: the TLC jar tracked, the proof checker's signature measured, the prover pinned by commit and digest | T-0045-14, 29, 31; `tools/TLAPS-PIN` | Practice | MEASURE 2.1 M |
| F8.6 | **Dated, frozen results files**, regenerated by drivers for the newer modules | `spec/README.md` | In part (item 78) | MEASURE 2.1 M |
| F8.7 | **Decomposition test**: a clause that can be superseded alone is a separate record | ToO §9 | Practice | GOVERN 1.4 M |
| F8.8 | **Assisted drafting declared**: four ratified and five pending texts drafted by the assistant, each saying so; no ADR-0029 criterion for it | ToO §0; G9 §4 | Open (item 66) | MEASURE 1.3 G |
| F8.9 | **The residual-risk statement** | `derived/topak-residual-risk-statement-2026.10.03.md` | Written 2026.10.03; numbers undeclared | MANAGE 1.4 G → P |

**Work items, not counted as features:** the deployment declaration template; the archetype-evolution record; the
ADR-0017 supersession; the `Paxos` module; the Observer and correlator as more than fixtures; the archive.

---

## 9. Correspondence summary

The inventory's tally at G9, by function:

| Function | Rows | M | P | C | G | X |
|---|---|---|---|---|---|---|
| GOVERN | 19 | 3 | 8 | 1 | 0 | 7 |
| MAP | 18 | 4 | 3 | 1 | 1 | 9 |
| MEASURE | 22 | 2 | 6 | 1 | 3 | 10 |
| MANAGE | 13 | 2 | 7 | 1 | 1 | 2 |
| **Total** | **72** | **11** | **24** | **4** | **5** | **28** |

**By principle.** P2 and P6 carry MANAGE, as on 09.15, and now with proofs behind them. P1 carries the TEVV rows and
moved three of them to M (MAP 1.6, MAP 2.3, MEASURE 2.1). P8 is the principle that grew most: the record corpus,
manifests and drift tooling answer MANAGE 4.3 and GOVERN 1.4 as a model, and are also the evidence for the one row
that fell (MEASURE 1.3: everything is one hand's). P7 is still where MEASURE lands and still the principle with the
most open features.

**What the 09.15 list could not say and this one can.** Eighteen features rest on proved invariants of a module (F1.5,
F1.6, F1.9, F1.10, F2.2, F2.5, F2.6, F3.2 to F3.4, F4.3, F5.4, F6.2, F6.3, F6.5, F7.1, F7.2, F7.4). None of those
is a proof about the running reference (F1.8).

---

## 10. Playbook practices not addressed

The inventory's §6 to §9 carry the lists: five gaps, four convertible rows, twenty-four partial rows with their
unaddressed half, twenty-eight out-of-scope rows by group. They are not repeated here.

---

## 11. Movement since 09.15, by feature

| 09.15 row | What happened |
|---|---|
| F1.6 "TLC vs TLAPS undeclared" | Declared (ADR-0046); fifteen modules proved |
| F2.6 "deployment profiles, axis unresolved" | Resolved as degeneracy (ADR-0023); the template still unwritten |
| F3.3 "promotion gate on a human signing key" | Replaced by a unanimous quorum grant with a veto seat (ADR-0024, A2) |
| F3.5 "Build effect stream undecided" | Decided (ADR-0021) |
| F4.3 "`Contained` vs `Mediated`, spec change" | Stated (ADR-0034 §4) and a lookup at the reference; still no member |
| F4.6 "LTRO decomposition" | Decomposed into seats and stages (ADR-0037, 0043) |
| F6.5 "exception mechanism, no owner" | Owned and proved (ADR-0013 §4, `NonComposition_proof`) |
| F6.1 / MANAGE 2.4 "!" | The contradiction corrected in the records (ADR-0003, ADR-0028); NC-2 proved |
| F7.1 "shared replicated Observer group" | Superseded: per-cell Observers and a correlator (ADR-0038) |
| F7.7 "monoculture declaration" | One pair per cell (ADR-0037); the independence criterion Proposed (ADR-0035) |
| F7.8 "quarantine gate" | Named (`K = 0`, ADR-0039 finding 1); still open |
| New since 09.15 | The lease as the credential (0031); the clock model (0032); the reference (0033); confinement (0034); the launcher (0036); coupling (0039); Run's four records (0040 to 0043); signed bundles (0044); the trusted base (0045); the method (0046) |
