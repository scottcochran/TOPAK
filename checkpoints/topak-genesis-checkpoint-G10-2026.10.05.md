# TOPAK — Genesis Checkpoint G10

**2026.10.05** · genesis custodian: Scott, (1, 0) · supersedes G9 (`228422d80155862b`) as the state of record · narrative: revision 13 of the Theory of Operation (`narrative/theory-of-operation.md`, `acee3f9df0135db1`, cut from G9, tag `ToO-rev13`) stands, **not revised at G10**, and is behind this checkpoint on labels, the tool list, operators, break-glass, the policy floor and the reference; where it and this checkpoint disagree, this document wins (§7, item 86)

**What G10 is.** The state of record, as G9 was: what each record says, what was ratified and by whom, what is owed,
and what is open. It is the first checkpoint that records a **provisional** record, and the first at which the
reference links a policy floor other than the genesis draft.

**What changed at G10.** Nine batches were ratified, **27 to 35**, where G9 had one. Five records drafted after G9
are in force: **ADR-0047** (the Listener labels what it delivers), **ADR-0048** (a Thinker learns its tools from the
mechanism), **ADR-0049** (the allowlist entry has one schema), and, **provisional**, **ADR-0050** (an operator is a
principal) and **ADR-0052** (break-glass is an emergency seating). With them twenty-six dependent amendments were
applied in seventeen accepted records. **X1, the floor's break-glass exception, is retired**; the floor's
exceptions are one. **ADR-0005** was ratified, discharging ADR-0033's oldest debt. **The Run profile is in force**:
ADR-0034 A2 with ADR-0042 §6, which is no longer Proposed. **R8 was withdrawn** and is not coming back as a TTL.

**"Provisional" is a status since Batch 34** (ADR-0029 A4): ratified, in force, subject to redesign, for a record
that did not meet its own ratification condition and says on its face what it lacked. ADR-0050 and ADR-0052 carry
it. **The policy floor is genesis-provisional** (ADR-0030 A3): gated, pinned and enforced, and ratified when the
bootstrap reviewer establishes that it is fit. That gives floor fitness an owner and a time, and no test.

**The reference was rebuilt in five stages** to follow the five records, and **switched outright from the genesis
floor to the proposed floor's `emergency` stage**, at the custodian's direction: labels and handles, the tool list
and its opening record, signed operator requests decided by nine control entries, and activation of an emergency
seating by the break-glass roster's quorum. **The unsigned operator socket is kept as a BOOTSTRAP path that seats and
does nothing else**; a first lease from a quorum, which is the centre of ADR-0050, is not built. **Proof
certification exists**: nineteen of twenty-two proof modules have every SMT obligation backed by a proof an
independent checker accepted. **Trace validation is current with the tree**, and exposed a race in lease expiry,
which is fixed. **No real principal is `Contained`**, as at G9. The bootstrap trigger is still unmet, and remains
optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2. Batches 27 to 31 on 2026.10.04; 32 to 35 on 2026.10.05.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **27 · Kafka** | 10.04 | **ADR-0005**, at R2 | Kafka is neither the ordering authority nor the system of record. C4: it discharges the debt ADR-0033 §2's K row carried since Batch 7 |
| **28 · The proof-checking backend** | 10.04 | **ADR-0046 E2 and A1** | E2: `tlapm -C` checks Zenon's proofs and nothing else. A1: T-0045-31 has a certified configuration, cvc5 behind `spec/smt-checked` with the checker of T-0045-14 in place of Z3 |
| **29 · The launcher's choices** | 10.04 | **ADR-0034 A3, ADR-0023 A1, ADR-0033 A7** | Four of the reference's PROVISIONAL choices written down; the declared rung is per seat (§6c); the launcher in the node. A7 ratified ahead of ADR-0036, which is still Proposed |
| **30 · The Run profile** | 10.04 | **ADR-0034 A2 with ADR-0042 §6**, at R4 | P4 for Run is channel fidelity; the tool host reads a tool's target from its allowlist entry. C2 and C4. ADR-0042 is accepted whole |
| **31 · Run's tools** | 10.04 | **ADR-0033 A8** | Run tools held to their channel at the reference |
| **32 · The declared target** | 10.05 | **ADR-0033 A9** | Split from a longer addendum so that the one row for text in force could be accepted alone. At `7764e52`, on the genesis floor |
| **33 · A race** | 10.05 | **ADR-0033 A13** | A lease just granted could be ended as expired; fixed. Split from A14 the same way |
| **34 · Five records** | 10.05 | **ADR-0047, 0048, 0049**; **ADR-0050 and 0052, provisional**; **twenty-six dependent amendments**; **ADR-0033 A10, A11, A12, A14**; **ADR-0029 A4, ADR-0030 A3** | The custodian chose to amend the conditions the reference had not met and ratify, over building first or ratifying the labels group alone, on three decisions: operators and emergency seating are provisional and subject to redesign; the bootstrap-set amendments are ratified with the genesis attestation covering them; floor fitness is ratified by the bootstrap reviewer |
| **35 · The two lists** | 10.05 | **ADR-0033 A15** | The rules' well-formedness reads the two issued lists; a test freed of the clock |

**Withdrawn, not ratified:** ADR-0026 A1 (R8, the break-glass TTL), pending since 2026.09.24, withdrawn by the
custodian on 2026.10.04 (W1). A break-glass grant has no timed expiry; it ends with its round.

### 1.1 Record status at G10

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | 0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part), 0019, 0020, 0022 (in part: §6 is Proposed), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | **26** | 0003 (for A2 only), **0005**, 0006, 0009, 0013, 0015, 0021, 0023, 0028, 0029 (for A2 and A4 only), 0030, 0031 (C2 for A1 only, beside its C1), 0034, 0037, 0038, 0039, 0040, 0041, 0042 (now whole), 0043, 0044, 0045, 0046, **0047, 0048, 0049** |
| **Accepted (genesis) · provisional** (confirmation required) | **2** | **0050, 0052** |
| Proposed | 3 | 0035, 0036, 0051; and ADR-0022 §6 |
| Superseded | 1 | 0008, by 0038 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

51 record files, numbered to 0052; six added since G9 (0047 to 0052). 0014 is the only reserved number.

**How the counts are read.** From each record's status line and status note together. ADR-0029's marking is in its
note and not on its status line: confirmation is required for A2, and since Batch 34 for A4, and for nothing else in
it. The four records of the bootstrap set (0024 to 0027) are accepted and cannot be confirmation-required (ADR-0029
§4); three of them now hold a provisional amendment (§1.2). 18 + 26 + 2 accepted, 3 Proposed, 1 superseded and 1
tombstone make the 51 files.

**No amendment is pending**, down from four. Every `**Pending:**` line in `decisions/` reads "none".

### 1.2 What is ratified in part, or with a scoped marking

- **ADR-0050 and ADR-0052 are provisional.** Each states in its ratification condition what its status carries.
  ADR-0050: a first lease from a quorum is not built, and no reader other than the drafter has reviewed it.
  ADR-0052: it rests on ADR-0050; a seating prepared by promotion is not built; two questions the reference raised
  are open (§7, item 92); no reader. Each stops being provisional when its debts are met and the custodian records
  it. **X1's retirement is in force on that basis.**
- **Three provisional amendments are in the bootstrap set**: ADR-0024 A3, ADR-0025 A3 and ADR-0026 A2. They are not
  confirmation-required, since confirmation runs under those records, and are covered by the genesis attestation,
  which must name them as provisional (ADR-0029 A4).
- **The twenty-six dependent amendments were applied as marked.** The dependent amendments were drafted to stand beside the text
  they change, and were applied by removing the pending mark, not by rewriting the sentences above them. Where one
  says a sentence above "becomes" or "gains" something, it does.
- **Every text ratified since G9 is the drafter's**, the assistant's at the custodian's direction, and each
  ratification row says it was not reviewed by a reader other than the drafter.

**Decided for the reference, not in a record**, at G9: six choices. **Five are now in records**: four by ADR-0034 A3
and one by ADR-0023 A1 (Batch 29). The sixth, a profile promoted as a one-file workspace, is in ADR-0036 at its R4,
and ADR-0036 is Proposed.

---

## 2. The floors as ratified

### 2.1 The rules floor

In force: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn; **R8 withdrawn** (ADR-0026 W1). **R6 and R7 change
subject** (ADR-0026 A2, Batch 34, provisional with ADR-0052): R6 still bounds the number of floor exceptions, and
the count it bounds is one; R7 is read as "no activation of an emergency seating grants a lease whose alphabet holds
an authority act", and with the `emergency` kind's alphabet as decided it has nothing to refuse.
**`RulesFloorBase.tla` has not caught up**: it still carries `bgScope` and a bound of two (§7, item 90). The rules
gain three issued things: an identity provider's key (ADR-0025 A3), and the two lists a bundle's load checks read
(ADR-0025 A2). The rules floor bounds none of them. The ADR-0026 §6 rerun is still owed.

### 2.2 The policy floor

**The entries in force changed for the first time since G7**, by ADR-0041 A1, A3 and A2 (Batch 34):

- **Three forbids over labels**: `R5-no-read-then-send`, `R6-no-steered-destination`, `R7-no-replayed-destination`.
- **Nine control entries** for an `operator` seat's six actions: `C1` to `C9`.
- **`X1-break-glass` is removed**, and `B10` lets a seat of kind `emergency` `Actuate`.

**The text is `floor/proposed/emergency-floor.cedar`** (`15c941b9a56a09f7`) with its schema (`d3c8145c6af2d9a3`):
28 policies, 107 cases, every gate passing on 2026.10.04. It is built in three stages from the genesis floor, each
gated: `labels` (20 policies, 74 cases), `control` (29, 106), `emergency` (28, 107). `floor/genesis-floor.cedar` is
unchanged and is the text the stages are built from.

**The floor is genesis-provisional** (ADR-0030 A3): not ratified by any batch, and ratified when the bootstrap
reviewer establishes that it is fit (ADR-0029 §5, step 6). **The stage files open with a comment that is wrong**:
"not what the reference follows". The bytes are kept as gated, so the digests the records cite are the digests the
reference pins (§7, item 91).

### 2.3 Confinement

**In force as at G9, and the two pending texts are ratified**: ADR-0033 A7 (Batch 29) and ADR-0034 A3. At the
reference nothing changed in what a lease above rung 0 rests on: rung 1 real, rung 3 SIMULATED, rung 2 a seam.
**An operator and an emergency seat are `Mediated`**: a person is not confined (ADR-0050 §1; ADR-0052 §1).

### 2.4 The LTRO

Unchanged since G7. ADR-0035 is still Proposed; it gained R4 to R7, three of them for the new records: an item
delivered as a handle is `ingress` and not `consumed`; a round's tool list is both; an operator's lineage is
declared, with its identity provider as root.

### 2.5 Run

**ADR-0042 §6 is in force** (Batch 30), with the Run profile. Run's ingress is **four items, each with a label**
(ADR-0043 A1): the task, consulted content, tool results and the tool list. **An item is delivered clear with its
label, or as a handle** with no bytes. A handle may be an argument; the tool host resolves it. **The floor carries a
minimum over labels** (§2.2), and a bundle cannot loosen it: delivering more in the clear buys a narrower round.
**The `Actuate` record's envelope** gains four label fields and says `seatKind` where it said `breakGlass`
(ADR-0042 A1, A2). **A round's topic opens with the tool list** the principal was given. **An emergency seat is not
coupled to an Observer** (ADR-0039 A2): `R3` is a Thinker's.

### 2.6 The trusted base

**In force, thirty-six rows**, up from thirty-one: T-0045-32 to T-0045-34 (the label computation and delivery; the
declarations, excluded; handle resolution and the list's rendering) and T-0045-35 and T-0045-36 (an operator's
identity provider; an operator's custody of its key). **T-0045-31 has a certified configuration** (ADR-0046 A1).
**Annex B's two paragraphs on the new rows were rewritten at ratification**: drafted when the reference had no
instance of them, ratified when it did. T-0045-24 is delegated at the archetype since Batch 30; Annex B kept it
excluded at the reference because the target was read from node configuration, and that reason ended with ADR-0033
A9 (§7, item 89). **The binding table has no rows** for `Labels`, `ToolList`, `Operators`, `Emergency` or the two
successor modules (§7, item 90).

### 2.7 Bundle signing, 2.8 the proof-carrying gate

Unchanged since G7. A bundle now also has to be well-formed to load (§3).

### 2.9 The proofs

**Twenty-two proof modules**, up from fifteen: `Labels`, `ToolList`, `Operators`, `Emergency`, `Correlator`,
`BreakGlass_A1` and `NonComposition_A1`. **5,225 obligations, every one proved.**

**Nineteen of the twenty-two certify** (ADR-0046 A1; `spec/proof-certification.md`): every obligation is closed by
the prover's own normalization, or by an SMT proof that the `ethos` checker accepted, or by a Zenon proof Isabelle
checked, or is a temporal step discharged by LS4, which no checker confirms. **Three do not**: `RulesFloorNV_rev5`,
`Confinement` and `Confinement_A1`. Restructuring them is deferred by the custodian (§7, item 74).

---

## 3. Verified artifacts

G9's artifacts keep their digests. New since G9:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| **`spec/Labels.tla`** and its proof | `cc124f5c406aedac` | ADR-0047 §11 | 37 TLC rows; ten properties, 651 obligations, certified. **The module found a hole in the record**: a literal laundered through an inside tool, closed by the join of ADR-0047 R10 |
| **`spec/ToolList.tla`** and its proof | `7c0a18b897e6cb98` | ADR-0048 §8 | 27 rows; five properties, 215 obligations, certified |
| **`spec/Operators.tla`** and its proof | `a465d7af62becd03` | ADR-0050 §10 | 32 rows; thirteen invariants, 354 obligations, certified |
| **`spec/Emergency.tla`** and its proof | `1abae9beb82b00fa` | ADR-0052 §9 | 51 rows; six properties, 373 obligations, certified |
| **`spec/BreakGlass_A1.tla`**, **`spec/NonComposition_A1.tla`** and their proofs | `b586a6afa4fd5136`, `d1e9113480d016bb` | ADR-0052 R5; ADR-0026 A2; ADR-0013 A1 | Successors where the predecessors model X1. 8 and 14 rows; 45 and 96 obligations, nothing assumed, certified. With the kind's alphabet as decided, dropping R7 changes nothing. A third mutation breaks NC-1 and NC-2: an activation's record kept only while its round is live |
| **`spec/smt-checked`**, `proof-cert.sh`, `proof-certification.md` | `bb86642633822ae5`; `61346a4237a85c94` | ADR-0046 A1 | The certified configuration and its method |
| **The floor stages** | §2.2 | ADR-0041 A1 to A3 | Each stage validated, tested and gated; a rerun reproduces each results file byte for byte |
| **The reference at `7764e52`** | manifest `SHA256SUMS-REF-2026.10.05` (`c395a8b85e5113a9`, 86 entries) | ADR-0033 A9 | 116 tests; on the genesis floor |
| **The reference at `c15026d`** | `-05b` (`920d06c557d56cb4`, 87) | A10 | 119 tests; the `labels` stage |
| **The reference at `c7de2ba`** | `-05c` (`03796b23d38fc7ca`, 89) | A11 | 126 tests; the `control` stage |
| **The reference at `9c57221`** | `-05d` (`7d2fbbd12df1c5f8`, 90) | A12 | 131 tests; the `emergency` stage |
| **The reference at `7d8c7db`** | `-05e` (`ad452379c32c3316`, 90) | A13, A14 | 132 tests |
| **The reference at `075b2e7`** | `-05f` (`41342e08e14b519c`, 90) | A15 | 133 tests across thirteen binaries; 38 Rego tests |
| **`spec/Mechanism.tla`** | `e29dbaf0936dbae1` | A14 | Models the label fold and the stale-`clearSet` refusal, a seating, the gate on unsigned requests, a control request with its facts recomputed and the envelope restated, an activation, and X1's approval rejected |
| **Trace validation** | `spec/Mechanism-trace-results-2026.10.05.txt` (`3b1ad26dfd432d48`) | A14 | **82 traces, 1,007 steps, every step matching**, and every state keeping `ConfinementRefinement.tla`'s invariants. Five edits that each removed one modelled thing produced a mismatch; a sixth is caught as an evaluation error |

**Frozen from G10 on**, as G9's are: the six new modules, their proof modules and their results files. `BreakGlass.tla`
and `NonComposition.tla` stay frozen; the `_A1` modules succeed them.

**Results the drafting did not anticipate**, since G9:

1. **A literal can launder what a principal has read.** ADR-0047's F2 and F3 were walked around in two calls: pass a
   literal to an inside tool that returns what it was given, then name that result by handle. `Labels.tla` found it;
   a result computed from a literal takes `clearSet` (R10).
2. **A lease just granted could be ended as expired.** A replica recorded when it saw a grant after releasing the
   state lock, and a lease with no observation reads as expired. Latent since the sweeper was built; shown when six
   operators were seated in a burst; found by the trace run and by no proof. Fixed (ADR-0033 A13).
3. **W10 could not be failed.** In ADR-0049's own form the fields it guards sit inside the input they describe.
   Restated at R4 to what can be checked.
4. **A lease cannot be narrowed to a tool.** ADR-0031 §1's schema is closed and carries no tool set, so ADR-0048's
   "a list of one" was restated at R6.
5. **An operator's seating feeds the emergency envelope.** The domain's envelope is every Run entry of every
   revision a seating in force names; an operator calls no tool and its seating still names one (§7, item 92).
6. **A person on an emergency seat is given handles unless the bundle says otherwise.** The delivery table is per
   seat kind, and the load check asks for no row for `emergency`.
7. **Parallel TLC runs collide** unpacking the standard modules into a shared temporary directory; two traces failed
   to parse for that reason and no other.
8. **A test of the backlog bound failed for the wrong reason** once its file held nine clusters: its tool calls
   could outlast one heartbeat's freshness. The refusal it met was correct; the test was freed of the clock.
9. **`tlapm -C` does nothing for an SMT obligation** (ADR-0046 E2), which is why a certified configuration was built.

**What these checks are.** As at G9, and: a certified proof still trusts the prover's translation of an obligation
into a query, its normalization, LS4, and the checker. A matching trace is not a refinement, and the model takes
more from the trace than it did: whether a request's signature is its seat's, whether a sign-on assertion verifies,
which roster keys approved an activation, which seat a revocation was lifted on. The floor's decision on an
operator's request is not modelled; the trace compares two restatements of the envelope, in Rust and in TLA+, and
neither with the Cedar text.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 28 records**, up from 22: the 26 of §1.1, which add 0005, 0047, 0048 and 0049 to
G9's 22, and the two provisional records, 0050 and 0052.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| As at G9 | as at G9 | Unchanged, with ADR-0034 A2 and A3 and ADR-0023 A1 added to records already marked |
| 0005 | C4 | That Kafka is transport only, and the debt of ADR-0033 §2's K row |
| 0047 | C4; C2 for §3 | The labels and the delivery rule; that a suppressed item's bytes do not enter the guest; F1 to F6 |
| 0048 | C4, C3 | Run's ingress as a closed list of four; the list as the only description with standing |
| 0049 | C4; C2 for §5 | The entry's form and its load checks; the entry as the one statement of a tool's channel |
| **0050** | C1, C3, C4 · **provisional** | Who may put a lease on the log. **And that the record is in force without its central behaviour built** |
| **0052** | C1, C3, C4 · **provisional** | The replacement of a privileged path, and the retirement of a floor exception |

**The ADR-0029 A2.5 line**, carried here for the first time; G4 to G9 did not carry it (the 10.02 critical review's
CR-28 (ii)).

| Field | Value at G10 |
|---|---|
| **Bootstrap reviewer engaged** | **None.** Every record, amendment, proof, module and reference tree is one hand's, drafted or ratified by the genesis custodian with the assistant; no reviewer independent of the author has read any record |
| **Last completed review pass** | **None.** No confirmation pass has been run and no review attestation exists; the field has no manifest digest to name. The dated reviews under `derived/` are the drafter's own and do not count under A2.1 |

**The bootstrap reviewer has two new duties** (ADR-0029 A4): to establish that the policy floor is fit, with which
it is ratified; and to attest to rules that include three provisional amendments, named as such.

**Bootstrap specification: partial**, as at G9. The ceremony gains the seating of the first operators, at least
three in each domain at the archetype (ADR-0029 A3, provisional), and floor fitness (A4).

**Debts no confirmation repays.** Those of G2 to G9 stand. G10 adds: **five records, twenty-eight amendments, six
modules and their proofs, a rebuilt reference and the model it is checked against are one hand's**, drafted, built,
checked and ratified across three days with no second reader; **two records are in force without meeting their own
conditions**, which is what provisional means; and **the reference was built to records before they were ratified**,
so for two days it followed text that was not in force and did not follow text that was.

---

## 5. Conventions carried at G10

G2 to G9's conventions stand. Added since G9:

- **Provisional is said wherever it applies**, as SIMULATED is: on the record's status line, in the index, in the
  register, and on any amendment that depends on a provisional record.
- **A record is ratified provisional only with its exit stated**: what was not built, and that it was not reviewed.
- **An addendum is split so that what is evidence for text in force can be accepted alone.** A9 from A10; A13 from
  A14.
- **An addendum ratified after the reference moved on says so in its opening paragraph**, and its body is left as
  drafted, speaking as of its drafting.
- **A proof is certified or its results file says why not.** `proof-cert.sh` accounts for every obligation by the
  route that discharged it.
- **A successor module takes the suffix `_A1`** and its predecessor, cited by digest, is not edited.
- **A model is checked to discriminate.** After a trace matches, the model is broken on purpose, one modelled thing
  at a time, and each break must show.
- **A dependent amendment is drafted to be applied as marked**, beside the text it changes.
- **BOOTSTRAP marks the unsigned operator path** wherever it stands in for a quorum or a promotion.

---

## 6. Records changed after their own ratification

Since G9:

| Record | Change | Why |
|---|---|---|
| 0009, 0013 | A1 each (B34) | Break-glass is an emergency seating; a grant ends with its round; the exception count is 1 |
| 0016 | A1, A2 (B34) | A person's Persona; the seat binding `emergency` |
| 0022 | A3 (B34) | The entry's form is ADR-0049's; a Thinker is told its tools |
| 0023 | A1 (B29) | The declared rung is per seat |
| 0024 | A3 (B34, provisional, bootstrap set) | A promotion seats |
| 0025 | A2, A3 (B34; A3 provisional, bootstrap set) | The two issued lists; the provider's key and the genesis seating |
| 0026 | W1; A2 (B34, provisional, bootstrap set) | R8 withdrawn; R6's count and R7's subject |
| 0029 | A3, A4 (B34) | The first operators at bootstrap; the provisional status, the attestation's cover, floor fitness |
| 0030 | A2, A3 (B34) | Label attributes in S and the allowlist's well-formedness; the floor is genesis-provisional |
| 0031 | A3 (B34) | Who grants and who denies |
| 0033 | A7 to A15 (B29, B31 to B35) | Nine addenda; none pending |
| 0034 | A2 (B30), A3 (B29) | The Run profile; four choices of the reference |
| 0037 | A2, A3, A4 (B34) | The Listener labels and delivers the list; the kinds `emergency` and `operator` |
| 0039 | A2 (B34) | An emergency seat is not coupled |
| 0040 | A1 (B34) | The root declares a label; the entry's form |
| 0041 | A1, A2, A3 (B34) | `R5` to `R7`; X1 retired; `C1` to `C9` |
| 0042 | §6 (B30); A1, A2 (B34) | Accepted whole; envelope fields and the opening record; `seatKind` |
| 0043 | A1, A2 (B34) | Four items, handles, what the Observer is given; what carries the task |
| 0045 | A1, A2 (B34) | Five rows; Annex B's paragraphs rewritten at ratification |
| 0046 | E2, A1 (B28) | What `tlapm -C` checks; the certified configuration |

---

## 7. Open list at G10

**G9's eighty-five items, as they stand.** An item not listed is as at G9.

| # | Item | At G10 |
|---|---|---|
| 1 | **The sandbox gap** | As at G9; A7 is ratified (B29). No guest passes P3, so no real principal is `Contained` |
| 2 | **Floor fitness** | **Owned and timed, with no test**: the bootstrap reviewer establishes it, and the floor is ratified with that (ADR-0029 A4; ADR-0030 A3). What makes a floor fit is not written (item 87) |
| 5 | **ADR-0005** | **Discharged** (B27) |
| 7 | **The archetype-evolution record** | Unwritten. The binding table is further behind (item 90) |
| 8 | **R8** | **Closed by withdrawal** (ADR-0026 W1). The bound on a break-glass grant is its round (ADR-0052) |
| 12 | **Derived documents** | Eight added since G9 and indexed |
| 14 | **The ToO** | Revision 13, cut from G9, stands; behind this checkpoint (item 86) |
| 20 | **The provenance independence criterion** | ADR-0035, Proposed, with R4 to R7 |
| 25 | **The genesis floor text and S**, DRAFT | **Changed**: the floor in question is the `emergency` stage, genesis-provisional, ratified at bootstrap (§2.2). The genesis text stays a draft and is what the stages are built from |
| 26 | **The Run profile** | **Discharged** (B30) |
| 34 | **ADR-0036's ratification run** | Open. ADR-0036 gained R4 to R6 and is still Proposed |
| 35 | **The launcher in `topak-node`** | Built, and A7 ratified (B29); ADR-0036 Proposed |
| 41 | **A seat-registration record** | Open; a seating is now a thing of record (ADR-0050 §2), made at the reference by the BOOTSTRAP path |
| 43 | **The correlator's detection function** | **Drafted**: ADR-0051, Proposed, with `Correlator.tla` proved and certified |
| 45 | **A scripted cell Observer; the scripted Run cell** | **The scripted Run cell is built** for labels (ADR-0047 §11), in a test, with a scripted Observer heartbeat |
| 46 | **`W(p)` as an ACL; the gate-side `K < R` check; A2.2 in the reference** | Open. Operators and emergency seats add readers that nothing gates: the mechanism has no read path for topics |
| 49 | **Break-glass under a dead Observer** | **Decided**: an emergency seat is not coupled (ADR-0039 A2; ADR-0052 §4), provisional |
| 56 | **The refinement chain, stages 2 and 3**; the reproducible build | Open. **Stage one is current with the tree** (A14) and found a race |
| 57 | **Gate evidence signed**; T-0045-13 changes class | Open. `AttestGates` is now attributed to an operator and is still an assertion |
| 58 | **ADR-0042 §6, the Run profile, channel fidelity's owner** | **Discharged** (B30, B31) |
| 59 | **The allowlist entry's schema** | **Discharged**: ADR-0049 (B34); the channel is declared once (A9) |
| 60 | **A record that lays out rounds** | Open. A round's topic now opens with a record the mechanism writes |
| 64 | **ADR-0023 §6b amendment; a deployment declaration template** | **In part**: §6c is in force (B29). The template is open |
| 66 | **An ADR-0029 criterion for assisted drafting** | Open, and resting on far more: every text ratified since G9 |
| 73 | **The prover pinned for reproducibility** | **Discharged**: `tools/TLAPS-PIN`; the wrapper refuses another binary |
| 74 | **The SMT backends' proofs checked** | **Discharged for nineteen of twenty-two modules**, by cvc5 and the `ethos` checker and not by Isabelle (ADR-0046 E2, A1). Three modules do not certify; restructuring them is deferred by the custodian |
| 76 | **The diagrams are not measured** | Open, and behind the tree |
| 78 | **One driver per TLC results file** | In part: every module added since G9 regenerates from a script |
| 79 | **Tags, and the narrative against this checkpoint** | **G9 was wrong here** (`checkpoints/README.md`, errata): the four tags it said were missing exist, and revision 13 was cut from G9 after it. Corrected in this cut. For G10: item 86 |
| 80 | **ADR-0034 A2 with ADR-0042 §6, then A8** | **Discharged** (B30, B31). T-0045-24 is delegated at the archetype; Annex B is item 89 |
| 81 | **ADR-0036's ratification, then A7** | **A7 ratified ahead of ADR-0036** (B29). ADR-0036 is open |
| 84 | **A Run tool's channel declared twice** | **Closed** (A9): the entry is the only declaration. The component realization and the protocol on a declared target remain |
| 85 | **Six choices of the reference accepted in conversation** | **Five in records** (B29); the sixth is in ADR-0036, Proposed |

**New since G9.**

| # | Item | Where it sits |
|---|---|---|
| 86 | **The narrative against this checkpoint, and tags.** Revision 14 and the glossary against G10: labels and handles, the tool list, the operator as a principal, break-glass as a seating, provisional, the floor's status. Tags owed: `G10`, and `REF-2026.10.05` to `REF-2026.10.05f` for the six trees the addenda cite | `narrative/`; `checkpoints/README.md` |
| 87 | **A test for floor fitness.** ADR-0030 A3 names who and when. Nothing names what | ADR-0030; ADR-0029 §5 |
| 88 | **The exit from provisional for ADR-0050**: a first lease from a completed tally, with a promoted seating; the first operators seated by an anchor issuance; a `Regrant` at rung 1 or above, which has to launch a guest; an operator's Persona record and lineage; a review | ADR-0050 §10; `mechanism/` I47 |
| 89 | **ADR-0045 Annex B, T-0045-24 at the reference.** Excluded there because the target was read from node configuration; A9 ended that | ADR-0045; ADR-0033 A9 |
| 90 | **`spec/` behind the records.** `RulesFloorBase.tla` still carries `bgScope` and R6's bound of two (ADR-0026 A2); no rows in the binding table for six modules; `Operators.tla` and `Emergency.tla` are tied to the reference by tests and no refinement | `spec/`; ADR-0026 |
| 91 | **The floor stages' opening comment is wrong**, and correcting it is a gate rerun and new digests in ADR-0047, ADR-0050 and ADR-0052 | `floor/proposed/` |
| 92 | **The exit from provisional for ADR-0052**: ADR-0050's; a seating prepared by promotion; whether an operator's seating is "a seating in force in the domain" for the envelope; whether a delivery table must have a row for `emergency`; a socket path for a person's signed action; something that counts the drill | ADR-0052 §9; `mechanism/` I48 |
| 93 | **What the label machinery trusts.** The label facts and an activation's envelope are the deciding replica's, and `apply` re-checks `clearSet` only; a failed call's error text reaches the principal unlabelled; a handle resolves only to a scalar, from results one replica holds in memory | `mechanism/` I46 |
| 94 | **What the reference does not follow in records now in force.** ADR-0049 §2's digest over the entry's inputs; a task at a first seating, and so its label; the two issued lists re-read when an issuance changes them | `mechanism/` I13, I46 |
| 95 | **A lease's tool narrowing.** ADR-0031 §1 carries none; ADR-0048 R6 leaves the question to it | ADR-0031; ADR-0048 |
| 96 | **Whether anything else a replica keeps beside the replicated state is recorded after the lock is released.** Not audited when the race was fixed | ADR-0033 A13 |
| 97 | **ADR-0051**, the correlator's folds, Proposed and not built at the reference | ADR-0051 |
| 98 | **Two policy comments call ADR-0049 Proposed.** A comment under `policies/` is part of the bundle's revision | `policies/` |
| 99 | **`REVIEWERS_GUIDE_README.md`** at the repository root, a draft written against G9, is behind this checkpoint. It is a convenience and not a record, and from this cut it is excluded from the manifest with the other README-class files, so that it can be kept current and pointed at the checkpoint in force | the root; `manifests/EXCLUDE` |

**Not on this list, deliberately:** bootstrap itself, as at G2 to G9.

---

## 8. What G10 does not claim

- **Nothing here is independently reviewed.** Nine batches were ratified on two days; the records, the amendments,
  the code under them, the modules, the proofs, the model and the runs are one hand's.
- **The operator design does not stand on evidence.** Its centre, that a first lease comes from a quorum, is not
  built. At the reference whoever reaches the socket can seat. That is why the record is provisional.
- **Break-glass has no settled form.** X1 is retired on a provisional record. If ADR-0052 is redesigned, there is
  none until the redesign is ratified.
- **No floor is ratified.** The entries are named by text in force and gated; the floor itself waits on a reviewer
  and on a test nobody has written.
- **A label is a declaration and not a finding.** It says what a source was declared to be. A source declared
  trusted that is not is seen by nothing, and the task's label is the operator's word.
- **No real principal is `Contained`**, as at G9. An operator and an emergency seat are `Mediated` by design.
- **Twenty-two modules' invariants are proved, nineteen with checked proofs, and nothing about the running
  reference is.** A matching trace is drift detection on tested paths; T-0045-28 stands.
- **A certified proof is not a verified one.** The prover's translation, its normalization, LS4 and the checker are
  trusted as written.
- **The reference is not the mechanism** (ADR-0033 §1).
- **The values are placeholders**, and **detection still fails open against a colluding Observer**. Operators
  observe each other by presence, not by anything read.
- **Bundles are signed under a throwaway key**; gate evidence is still an assertion, now with a name on it.
- **The narrative is a revision behind**, and further behind than at any earlier cut (item 86).
- **No deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G10` · 499 entries, cut from commit `e4b174e` plus this checkpoint and the edits that go with it.

As at G2 to G9, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it; both are recorded where they are cut, in the commit that adds them, and `manifests/index.tsv` names that
commit so `tools/verify-manifest.sh --all` checks this manifest at the tree it measured.

| Area | Entries |
|---|---|
| `decisions/` | 51 records |
| `checkpoints/` | 11 — the v1 corpus manifest, G1 to G10 |
| `narrative/` | 12 — G9's 11, and `architecture-description.md` |
| `derived/` | 29 dated artifacts — G9's 21 and eight more |
| `spec/` | 172 — G9's 102, and seventy more: seven modules, seven proof modules, their TLC, proof and certified-proof results, the certification wrapper and its method, row files and run scripts, and the 10.05 trace results |
| `floor/` | 146 — G9's 132, and fourteen under `floor/proposed/` |
| `process/` | 6 logs |
| `manifests/` | 17 — sixteen reference manifests and the `slm/` tree manifest |
| `tools/` | 55 — G9's 54, and `TLAPS-PIN` |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24` through `-2026.10.05f`; the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those seventeen in turn. No reference manifest is cut at G10:
since `075b2e7`, `mechanism/` changed in two files, the pin file (ADR-0033's pin, with A15) and the register, whose
header now names G10.

Verify from the repository root, at this checkpoint's commit:

```sh
shasum -a 256 -c manifests/SHA256SUMS-G10 | grep -c ': OK$'                 # expect 499
tools/verify-manifest.sh --all                                              # every manifest at the commit it measured
```

**`SHA256SUMS-REF-2026.10.05f` fails two entries at today's tree, and should**: it measures `075b2e7`, and the pin
file and the register moved after it. It verifies 90 of 90 there. Each earlier reference manifest of 2026.10.05
fails more, for the stages after it, and verifies whole at its own commit.

**`SHA256SUMS-G9` fails at today's tree, by construction**: twenty-six records changed, with the narrative, the
binding table's neighbours under `spec/`, `Mechanism.tla` and the trace scripts. It verifies 392 of 392 at
`97a61e8`.

The manifest excludes what `manifests/EXCLUDE` lists, as at G9, and one file more: `REVIEWERS_GUIDE_README.md`
(item 99), added to the list at this cut. `diagrams/` stays excluded (item 76). `mechanism/`,
`policies/` and `slm/` are measured by their tree manifests, not directly. Generated `spec/Trace_*.tla` files are
ignored by git and are not measured.
