# TOPAK — Design-gap assessment

**2026.10.03** · derived · **the gaps that are in the design, not in the build**, with independent review set aside ·
against Genesis Checkpoint G9 (2026.10.02), Theory of Operation revision 13, `mechanism/GAPS-AND-ASSUMPTIONS.md`,
`decisions/README.md` and the tree at `7075169` · drawn from `topak-residual-risk-statement-2026.10.03.md` §1,
`topak-critical-review-2026.10.02.md` (CR-27 to CR-39 and the re-grades), `topak-assessment-2026.10.03.md` and §5 of
`topak-competitive-design-assessment-2026.10.01.md` · prepared by Claude at the custodian's request

**What this is.** The corpus keeps three kinds of gap in the same lists: things the design specifies and the reference
does not build, things no reviewer other than the author has read, and things the design itself does not yet say. This
document is the third kind in one place. Nothing here is new: every row cites the finding, gap or open-list item it
comes from, and a reader who wants the argument reads the source. It is a derived document and not a record; nothing
here is ratified.

**The test for a row.** A gap is in the design if building everything the records now specify, exactly as written,
would leave it open. That admits four cases: no record covers it (§1); a record covers it and is not in force (§2);
the formal layer does not state it (§3); or the design leaves a value to a deployment and no value is declared (§5).
§4 lists the places where the design chose not to close a gap, because those are positions and should not be read as
debts.

**What is left out, and why.**

- **Independent review.** Excluded by the question this document answers. It is still the gate on §2: the pending
  texts were drafted, built, checked and proved by one hand (residual-risk statement §1.5; CR-33), so ratifying them
  without a second reader closes the row in letter only.
- **Specified and not built.** The sandbox gap's mechanism half (G1; the design half closed with ADR-0034 on 09.28),
  replica and operator authentication (G5), the archive and the forensic horizon (G9), erasure (G11), the Observer and
  quarantine gate as producers (G12), write-time masking, rungs 2 and 3. The records say what each is; the reference
  does not have it.
- **Trusted as written.** The Cedar engine, TLC at the constants run, the prover's backends without certificates (G9
  item 74), practical constants (item 75). These are verification debts on a design that is stated.

---

## 1. No record covers it

Each row needs a record written before anything can be built or ratified.

| # | Gap | What is missing | What would close it | Source |
|---|---|---|---|---|
| 1.1 | **Prompt injection inside the envelope; no flow constraints on arguments** | The floor bounds what can happen. Nothing bounds what an injected Thinker will do inside that bound: an injected Run principal may `Actuate` to any target the floor allows with those argument types | A record for provenance labels on `Consult` and `Actuate` arguments as syntactic lift, in ADR-0007's terms. A sketch exists; it has no owner and no open-list item. **Note, 2026.10.03, after this document's basis:** ADR-0047 was drafted the same day and is Proposed. It labels Run's ingress at the Listener, delivers suppressed items as handles, and requires a floor minimum (F1 to F6). On that tree this row reads as a §2 row, a record not in force; the counts below are left as they stood at `7075169` | CR-6, CR-32; residual-risk §1.8; competitive assessment §5 item 2 (A14) |
| 1.2 | **Tool descriptions are unpinned** | Tool code is pinned by digest. The interface text a Thinker reads is ingress that no allowlist entry names, so it can be poisoned with no change to the code | The digest of a tool's interface text in its allowlist entry; it lands in the entry schema ADR-0040 leaves open, and is independent of 1.1's fix. **Note, 2026.10.03, after this document's basis:** ADR-0048 was drafted the same day and is Proposed. Reading the reference showed that an allowlisted tool has no interface text on the record at all, so the record has the entry carry its interface and the Listener deliver the tool list. On that tree this row reads as a §2 row | CR-32; competitive assessment §5 item 4 |
| 1.3 | **Delegation, chains and attenuation** | A principal cannot create a subordinate, so there is no chain to bound and no cascade to model. TACIP 3.8.3, 4.4.2, 5.3.2, 8.1.5 and 13.2.2 presuppose one. Four reviews have said so | A record that either models delegation or states its prohibition as the position, with what a deployment that needs sub-agents does instead | CR-3; G9 item 51 |
| 1.4 | **The correlator's detection function** | The correlator has a seat kind, a placement rule and a read set, and computes nothing. Sequence numbers on denials, its cheapest input, are also open | A record defining what it computes and over what store. **Note, 2026.10.03, after this document's basis:** still no record. ADR-0047 and ADR-0048 (Proposed) give it inputs it can read without payloads: label fields on every `Actuate` record, and the digest of each round's tool list. A first function is statable over them; the function, its store and sequence numbers on denials are still missing | G9 items 43 and 44; residual-risk §1.3 |
| 1.5 | **History-dependent policy** | A temporal condition is either a mechanism constant, changed by a mechanism release, or unanalysed Rego. There is no policy-tier semantics for it | A decision on whether temporal conditions belong at the policy tier, and if so their semantics. **Note, 2026.10.03, after this document's basis:** partly answered by precedent. ADR-0047's `clearSet` (Proposed) is a history-dependent attribute computed by the mechanism as a monotone fold and read by policy as an ordinary attribute. Each such fold is a mechanism release, and it is scoped to one round. The open question is now a fixed set of mechanism folds against folds that policy may declare | Competitive assessment §5 item 3 (A15) |
| 1.6 | **The operator channel is untyped** | Principals' actions are typed, lifted, floored and bundled. `grant`, `launch`, `revoke`, `issue`, `GatesPassed` and profile registration have no comparable discipline, and this is the half of the control plane that can add authority | An alphabet and floor treatment for operator requests. Authenticating the socket (G5) is a build item and does not supply the types. **Note, 2026.10.03, after this document's basis:** still no record, and the stakes are higher. ADR-0048 (Proposed) moves tool descriptions off this channel and into the promoted bundle. ADR-0047 (Proposed) puts the task's label on it: the label must be present and nothing checks it, and the label forbids start from it. ADR-0049's method, each field marked checked or claimed and malformed data refused at load, is one this row could reuse. **Note, 2026.10.04:** ADR-0050 is drafted and Proposed: an operator is a principal of a fourth seat kind, seated by promotion, renewing within its domain under a lease and able to deny without one. On that tree this row reads as a §2 row | CR-34; residual-risk §1.4 |
| 1.7 | **Who runs the gates, and how their evidence is attested** | Gate evidence is an operator's assertion (T-0045-13, excluded), so every promotion theorem that assumes the gates ran is void | A record naming the gate runner and the evidence signature; T-0045-13 then changes class | G8; G9 item 57 |
| 1.8 | **Floor fitness** | The floor is shown well-formed and non-vacuous. Nothing says it is the right floor. No gate and no owner since G1 | A fitness criterion and a gate for it (MEASURE 2.13) | G16; residual-risk §4 |
| 1.9 | **Genesis rules and the bootstrap spec** | The reference starts from development rules, which are not genesis rules | The bootstrap specification and a genesis rules file under custody | G6 |
| 1.10 | **Re-genesis migration** | A new chain inherits no forensic read access to the old one; the chain id appears in topic names only | A migration record | G17 |
| 1.11 | **Log compaction and snapshots** | The log and its companions grow without bound, and no record says how a snapshot preserves what the theorems read | A compaction record. This is the smallest row here, and it is a service concern more than a safety one | G14 |

---

## 2. A record covers it and is not in force

The text exists. Each row needs a decision, and by the note above a reader who is not the drafter.

| # | Gap | State | Consequence while open | Source |
|---|---|---|---|---|
| 2.1 | **Channel fidelity for Run** | ADR-0034 A2 pending, with ADR-0042 §6 Proposed; A8 follows | Run principals are `Mediated` by the records whatever the lookup computes. The reference narrowed all three of A2's drafter's choices: the Wasm component became a core module, the protocol is recorded and not enforced, and a Run tool's channel is declared in bundle data and in node configuration with nothing checking the two agree | CR-33; G19; I43, I44 |
| 2.2 | **The rung-1 launcher** | ADR-0036 Proposed; A7 follows | The launcher is cited by nothing in force | Assessment §2 item 3 |
| 2.3 | **The independence criterion** | ADR-0035 Proposed; `Rules.criterion` unset in every shipped rules file; five lineage thresholds unset | Even a real rung 3 is not `Contained`. The veto seat's independence is declared and not checked (G18). Collusion's only structural cover has no force | G2; G18; residual-risk §1.3 |
| 2.4 | **Break-glass TTL** | R8 (ADR-0026 A1) drafted, pending, four conditions unmet | An approval is time-unbounded within an epoch. Ratifying it makes `Anchor_proof` and `BreakGlass_proof` stale (ADR-0046 E1) | CR-29; G10; G9 item 8 |
| 2.5 | **Break-glass under a dead Observer** | Ratified as written (ADR-0039 R4); G9 item 49 open | Floor entry R3 couples every effect-bearing Run admit to a live Observer, break-glass included, so the emergency path waits on the thing that failed. This one needs a decision against a text in force, not a ratification | CR-29; residual-risk §1.9 |
| 2.6 | **Six reference behaviours accepted in conversation** | Carried as PROVISIONAL tags; owed to ADR-0023 §6b's template and ADR-0034 | The reference does things no record says | G9 §1.2, item 85; I37 to I42 |
| 2.7 | **Kafka's role** | ADR-0005 Proposed | The record planes are described by a record not in force | `decisions/README.md` |

---

## 3. The formal layer does not state it

| # | Gap | What is missing | Source |
|---|---|---|---|
| 3.1 | **No liveness property anywhere** | Every module is `Init /\ [][Next]_vars` without fairness, and every property is an invariant. Run's posture under a lagging Observer is "stall", and the model cannot tell a stall from a deadlock. One property under weak fairness on the heartbeat in `Coupling.tla` would be the first | CR-37; `spec/proof-method.md` §5 |
| 3.2 | **No refinement to code** | Every property for a running deployment is conditional on T-0045-28. The trace harness is stage one and covers tested paths only. The design names the debt, an owner and a first stage; the chain itself is not designed, and no reproducible build fixes what was traced (T-0045-30) | CR-4; residual-risk §1.6; competitive assessment §5 item 1 |
| 3.3 | **Observer collusion** | Three of four detection failures close by mechanism. In the fourth, every liveness fact is the Observer's own heartbeat and watermark, so one that lies about keeping up is indistinguishable from one that does. Declared open (ADR-0039 §5; ToO A13). Rows 1.4 and 2.3 are the two covers and neither is in force | CR-2; residual-risk §1.3 |
| 3.4 | **Finding 8's model** | Closed in the records with ADR-0031 E1; the bootstrap `Promotion` module still owes the model | `mechanism/GAPS-AND-ASSUMPTIONS.md` §4 |

---

## 4. Positions: gaps the design chose not to close

These are stated trades. They belong in any external comparison and should not be scheduled as work.

| # | Position | Cost | Source |
|---|---|---|---|
| 4.1 | **Replicas are crash-fault, not Byzantine.** BFT considered and declined (ADR-0045 §6) | A compromised replica can propose an admit no floor evaluated; apply-time re-check stops stale admits and not forged ones. Mutual authentication stops impersonation only | Residual-risk §1.7 |
| 4.2 | **No resumption.** A crashed round ends | The work is lost. The Theory of Operation states the capability cost of confinement and not of durability; long-horizon Run tasks will meet it. The statement is owed at the next checkpoint | Competitive assessment §5 item 6 |
| 4.3 | **The trusted base is thirty rows** | The audit surface grows with scope | Competitive assessment §5 item 5 |
| 4.4 | **Replay is boundary events only** (ADR-0020) | The forensic record and TACIP 8.2's root-cause requirement pull in opposite directions, and the corpus has not said which way it leans; a deployment claiming root-cause capability has to say what compensates | CR-38 |
| 4.5 | **Rung 1 trusts the host** | By construction; both rung-1 profiles declare a failing conjunct and say so | Residual-risk §1.4 |

---

## 5. Left to a deployment, and nothing is declared

The design is complete in form here and empty in value. The proofs quantify over these and cannot choose them.

| # | Value | State | Source |
|---|---|---|---|
| 5.1 | `T_obs`, `K`, Run's `R`, `T_persona` | Placeholders (5000 ms, 8, 64, one hour). No Observer has been measured; `L`, the detection latency, is unmeasured. The `slm/` rig could measure `T_obs` and `K` | CR-36; G9 item 47 |
| 5.2 | The anchor custody threshold | No deployment has declared one, so the capture coalition is one key-holder | Residual-risk §1.1 |
| 5.3 | `T_irrev` per effect class | Declared for no class | Residual-risk §5 |
| 5.4 | The bundle signing key's custody row | Undeclared; signing at promotion is a script step with a development key | G7 (retired), G9 item 67 |

---

## 6. Reading the lists together

- **Rows 1.1 and 1.2 share a place and not a fix.** Both are about what the Listener hands the Thinker, and both are
  mechanism-computed, so ADR-0007 holds for each. Row 1.2 is cheap: a digest in the allowlist entry. Row 1.1 is not:
  labels cannot follow a value through the model, so it needs handles or a split of the cell. The 10.02 review calls
  the labels record the highest-leverage single record available.
- **Collusion is one gap in three rows.** 3.3 is the open case, 1.4 is the detector with no function, and 2.3 is the
  independence rule with no force. Closing any one alone does not close it.
- **The authority-adding surface is the least designed.** Rows 1.6, 1.7 and 1.9 are all on the operator side.
- **Two rows are decisions and nothing else.** 2.4 and 2.5 are small, both sit on the break-glass path, and 2.4's proof
  cost is known in advance.
- **§2 loops back to what this document excludes.** Every pending text there has one author, so the count of rows that
  can be closed well without a second reader is smaller than the table suggests.

Counts: eleven rows with no record, seven with a record not in force, four in the formal layer, five positions, four
undeclared values.
