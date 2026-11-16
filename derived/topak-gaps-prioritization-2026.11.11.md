# TOPAK — Gaps prioritization

**2026.11.11** · derived · a plan offered, not a record · basis: the tree at commit `bbda621`, Genesis Checkpoint G11,
and the four documents written with this one as the self review of 2026.11.11: `topak-critical-review-2026.11.11.md`
(CR-40 to CR-61), `topak-open-findings-register-2026.11.11.md`, `topak-feature-list-2026.11.11.md` and
`topak-residual-risk-statement-2026.11.11.md` · supersedes `topak-gaps-prioritization-2026.09.28.md` as basis, which was
written against G4 and was the plan the 09.30 batches followed · prepared by the assistant at the custodian's
request

Nothing here is ratified, nothing here is a decision, and **nothing here has been done**. The review's brief ended
at findings. This document orders what could follow, says what is ripe to ratify and what is not, and hands over
each class of fix with where its rows are. Every entry is suggested, and none is made.

**Not independent.** The order is the drafter's, built on a review by the drafter's lineage. The first item below
is the one thing that would change that.

---

## 0. In one paragraph

The corpus does not need more text. It needs the text it has to be made true of the tree, cut, and read by
someone else. Three things come before any new drafting: **a reader who is not the author**, **a checkpoint**, and
**a decision on what an overlay record is**. After those, one batch of errata carries the Batch 34 retirement
through the five places it missed and takes the stale "pending" marks off text that is in force. Then the Proposed
set, oldest first: ADR-0035 decided, the specification graph rebuilt and its record revised, workflows reconciled
with their module and their code, and the overlay last, because it rests on all of them. **No Proposed record is
ripe to ratify as it stands** (§2).

---

## 1. The order of work

By leverage per unit of work. "Whose" says who can do it: only the custodian (a decision), the drafter (text or
tooling, for the custodian to ratify), or someone else (a second person).

| # | Do | Why here | Closes or moves | Whose | Size |
|---|---|---|---|---|---|
| 1 | **Engage one reviewer who is not the author**, record it on the A2.5 line, and give them the register, the ledger and the review's §9 | It is the only item that moves MEASURE 1.3 and every "a reader who is not the drafter" condition in eighteen Proposed records; first on 09.25, 10.02 and now | CR-61, CR-28, CR-21, CR-5; the reader item of every ratification condition | Someone else, engaged by the custodian | Recruiting, then one to two weeks of reading |
| 2 | **Cut G12 at the tree as it is, before changing anything** | One cut measures 190 files, puts Batches 38 and 39 in the state of record, and gives the reviewer of item 1 "one named manifest digest" (ADR-0029 A2.1). A cut is also the only time stale sentences have ever been fixed | CR-41, CR-55 in part, CR-58; 59 open stale-sentence rows of the register | Custodian, with the drafter | One to two days: checkpoint, revision 16, glossary, both guides, three indexes |
| 3 | **Decide what an overlay record is**, in ADR-0029's terms: a status class and what happens to C3, or the answer that there is none and the ten are ordinary Proposed records | Ten records' ratification paths run through one sentence the process does not have. Nothing in the overlay should be revised again until this is settled, or the revision is to text whose standing is unknown | CR-40; the ratification path of ADR-0058 to ADR-0068 | Custodian | A decision, then an amendment to ADR-0029 or ten status notes |
| 4 | **Batch 40, errata: carry Batch 34 through** | Five places still describe break-glass as a floor exception, one of them the exhaustive classification that earns ADR-0015 its C2, and one a proved invariant's clause | CR-45; CR-43 in part | Drafter drafts, custodian ratifies | One day. ADR-0015, ADR-0043 §2, ADR-0029 §5, a successor to `RulesFloorBase.tla`, `rules.rs` |
| 5 | **Batch 40, errata: say what is in force** | ADR-0041 §1's tables, three READMEs, one index and the History State columns each tell a reader that text in force is pending or a draft | CR-47, CR-44 | Drafter drafts, custodian ratifies the record errata | Half a day for the living files; an erratum each for ADR-0041 and the four records whose status line lacks a C3 |
| 6 | **Decide ADR-0035: ratify it, or take ADR-0024 A2.2 and its dependents out of force until it is** | A clause of the bootstrap set's promotion rule rests on a record Proposed since 2026.09.25 and is enforced nowhere | CR-42; the residual-risk statement §1.16 | Custodian | A decision. Ratifying it as its own condition is written needs item 1's reader: one of the five conditions is a review by someone other than its author |
| 7 | **Put the emergency seat's rule in the floor, or say in ADR-0052 that it is the mechanism's** | The floor in force decides `Renew` and `Regrant` of an emergency seat *allow*; one forbid and one case close it | CR-46 | Drafter drafts the entry and the gate run; custodian decides which | Half a day |
| 8 | **Make the four checkers fail when they find something**, and add `skills/` and `diagrams/` to the reference checker | Hours of work, and every later item is checked by them | CR-57 | Drafter | Hours |
| 9 | **Rebuild the specification graph at the cut, pin tracked inputs only, and revise ADR-0057 and ADR-0058** | The graph has no node for sixteen `.tla` files or ten records, cannot be reproduced from a checkout, and grades every theorem *trusted* against what ADR-0058 states | CR-52; the precondition of ratifying ADR-0057 (§2) | Drafter | One to two days |
| 10 | **Binding-table rows for the twenty-one modules that have none** | The inventory every deployment is to compute says nothing of labels, tools, operators, the emergency seating, liveness, workflows or the overlay | CR-54; G11 item 90, open since G10 | Drafter | Two to three days; mechanical for the proved modules |
| 11 | **Reconcile ADR-0054 and ADR-0055 with `Workflow.tla`, `Mesh.tla` and `workflow.rs`, then prove the two modules** | The reference runs a third thing. Each of the five disagreements is a decision about which of record, module and code is right | CR-50; G11 items 101 and 56 | Custodian decides each; drafter revises | Three to five days with the proofs |
| 12 | **One revision of the overlay's records, with the diagram findings and this review's two readings side by side** | 68 standing findings from this review's two readers, eighteen diagram findings (sixteen open, two partly addressed), and six findings of the two assessments of the proposal still open, all against the same ten files. ADR-0068 has never been revised | CR-48, CR-49; the register §2.9 to §2.11 | Drafter, after item 3 | Two to three days. Successor modules for what the records say and no module states (the effects that are not charged, a lease's `ttl`) are a further week if wanted |
| 13 | **Disposition the register** | 252 open rows, 108 carried nowhere. Most are one line each; a disposition is applied, declined with a reason, or carried as named debt | CR-60 | Custodian | A week of reading, less with item 1's reader |
| 14 | **Then, and only then, the 10.02 review's standing asks**: an image that passes P3; a first lease from a quorum; measured `T_obs` and `K`; a `Mechanism.tla` that models workflows; the coupling leads-to properties proved | None has moved since 10.09, and none is blocked by anything above | CR-27, CR-36, CR-37, CR-55; the residual-risk statement §8 | Drafter builds; custodian declares the numbers | Weeks |

Items 2, 4, 5, 7 and 8 are about a week of work and add no design. Items 1, 3 and 6 cannot be scheduled by the
drafter: one is a person and two are decisions.

---

## 2. What is ripe to ratify, and in what order

Read from each record's own ratification condition, the review's evidence table (§5.1) and the findings against
it. "Layer" is the dependency order of the review's §5.2.

| Record | Layer | What its own condition still lacks | What the review found | Ripe? |
|---|---|---|---|---|
| ADR-0022 §6 | | A principal that passes the confinement profile | Its header says "undelivered" where two of its History rows and ADR-0034 say discharged | **No.** Waits on ADR-0036's run |
| ADR-0035 | 0 | Its five conditions carry no state and its θ values are unset; one condition is a review of the bounded-share construction by someone other than its author | Its tally rule was ratified into ADR-0024 as A2.2 and is followed nowhere (CR-42) | **A decision, not a readiness question** (§1 item 6) |
| ADR-0036 | 0 | The ratification run on an image that passes P3 | §6 still says the launcher is a script "today"; none is under `slm/`, and its own fifth revision says the move is done | **No.** The 10.02 review's second ask, still open |
| ADR-0051 | 0 | The reference; dependent entries undrafted | Rests "C3 does not apply" on a reading ADR-0038 §3 contradicts; makes two correlators the archetype with no change to ADR-0038; its proved properties cannot express a false finding (CR-53) | **No** |
| ADR-0054 | 0 | Proofs; several modelling gaps it lists | Record, module and reference disagree in five places (CR-50) | **No.** After §1 item 11 |
| ADR-0055 | 1 | Proofs; dependent entries undrafted; the gate | Four of six conditions carry no state | **No.** After ADR-0054 |
| ADR-0056 | 0 | Everything: no module, floor entry, reference path or dependent entry | Contradicts itself on the subject assertion (CR-51) | **No.** A first draft |
| ADR-0057 | 0 | Its §14 is marked Met | The Met no longer holds at this tree; the graph does not hold what §3 to §5 say (CR-52) | **Nearest of the new records, and not yet.** After §1 item 9 |
| ADR-0058 | 1 | All four conditions; none has a state | Not revised after ADR-0057's first revision | **No.** After ADR-0057, and it must say what item 3 decides |
| ADR-0059 to ADR-0066 | 2 to 7 | The floor stage; the reference; a reader; and for ADR-0060 and ADR-0066 the exits of the two provisional records | CR-40, CR-48, CR-49 | **No.** Last. Each rests on ADR-0058 and, through ADR-0060 and ADR-0065, on the workflow pair |
| ADR-0067 | 8 | Fourteen entries, and a fifteenth on one option of ADR-0060 §5, in prose and none in Cedar; "a floor is ratified", which is the bootstrap reviewer's finding | Entries lag the first revision in three places | **No**, and not before bootstrap as its condition is written |
| ADR-0068 | 9 | A property named for each bound; waits on ADR-0067 | Never revised; still says no module is written | **No** |

**The order, if the custodian wants one.** G12 first, with nothing ratified in it but what is already in force.
Batch 40 as errata only (items 4, 5, 7). ADR-0035 decided. Then ADR-0057 after its rebuild, alone; ADR-0058 after
the overlay question. Then ADR-0054 and ADR-0055 together, with proofs. Then, if the overlay is to be anything
but a proposal, ADR-0059 to ADR-0066 as one set after one more revision, and ADR-0067 and ADR-0068 after bootstrap.
ADR-0036, ADR-0051 and ADR-0056 wait on building, not on reading.

**What should not be ratified to tidy the picture.** The overlay, on the strength of its proofs. The proofs are
real and reproduce; the records say more than they prove (CR-48), reverse accepted text they do not name (CR-49),
and stand on a status the process lacks (CR-40).

---

## 3. The fix classes, handed over

Each is a class of change the review found and did not make. Rows are in the register (Part III unless said) and,
in full, in the annex's `findings/`.

| Class | What it is | How many, and where | Needs |
|---|---|---|---|
| **Stale sentences in living files** | A status, count, date or "not yet" the tree has passed, in the narrative, glossary, guides, READMEs, indexes and pins | 77 standing findings against living documents (readers K1 and K2 mostly), and 59 open stale-sentence rows of Part I, the 11.05 list's twenty-two among them | The drafter, at the cut. No ratification |
| **Errata to records in force** | A sentence in an accepted record that another accepted record, or the record's own later rows, have overtaken | 205 standing findings whose basis is text in force; CR-44, CR-45, CR-47 and CR-56 gather them | A typed History row each, in a batch |
| **Revision rows for Proposed records** | Revisions before ratification: ADR-0054 to ADR-0058, and the overlay | 143 standing findings against Proposed or pending text, 68 of them the overlay's two readers'; with the register's §2.9 (eighteen diagram findings) and §2.10, §2.11 | The drafter, after §1 item 3 for the overlay |
| **Evidence and tooling** | Module headers, results-file headers, checkers, the graph, the register of the reference | 60 standing findings whose basis is evidence; CR-52, CR-55, CR-57 | The drafter. A frozen module gets a successor, not an edit |
| **Decisions** | Where two texts disagree and only the custodian can say which stands | §4 below | The custodian |
| **The cut** | G12, revision 16, glossary terms for the specification graph and, if it is kept, the overlay; tags; the manifest | §1 item 2 | The custodian, with the drafter |

---

## 4. Decisions only the custodian can make

In the order they block other work.

1. **What is an overlay record?** (CR-40.) A class in ADR-0029 §3 with its own rule for C3; or no class, and C3 on
   each of the ten.
2. **ADR-0035: in or out?** (CR-42.)
3. **Is the emergency seat's one-round rule floor material or mechanism?** (CR-46.) ADR-0050 says the floor states
   the envelope.
4. **Which is right for a lapsed worker lease, a finding against an ancestor, and a refused grant**: the record,
   the module or the reference? (CR-50.) Five small decisions.
5. **Is the subject assertion on the record?** (CR-51.) ADR-0056 §5 says no and §7 says yes.
6. **Is a rung declared per deployment or per seat?** (CR-53.) ADR-0023 §6c says per seat; ADR-0034 and its
   modules say per deployment.
7. **Does an intent's budget draw down the seating's, or start afresh?** (CR-48.) The records and the module say
   afresh; ADR-0059's field says "may ever issue".
8. **Which of ADR-0060 §5's three options stands for an unattended plane?** Open since the second revision, with
   one answer already drafted into ADR-0062 and `FD15`.
9. **Do the exits from provisional follow the records or the checkpoint?** They differ (F-4).
10. **Should a derived document's findings have a path into the open list?** (CR-60.) Today they have none:
    252 rows of the register's first part are open, and 108 of those are carried nowhere.

---

## 5. Easy wins

Each is hours, mechanical, and waits on no decision.

- A non-zero exit from `tools/verify-manifest.sh` and `spec/mechanism-trace-run.sh` on a failure; `skills` and
  `diagrams` in `tools/check-refs.py`'s pattern; its header count taken from the de-duplicated list (L-1, L-2,
  L-8, L-11).
- `spec/proof-results.sh` reading the base module's `ASSUME`s as well as the proof module's (I1-2). The three
  results files it would change are cited by digest, so they get successors.
- A reason line for `Workflow.tla` and `Mesh.tla` in `spec/proof-sync.sh`, so that it exits 0 when nothing is
  out of step (G11 item 101).
- The decisions index: the column header, which still reads "Status at G8", and the confirmation markings of
  eight records (CR-44).
- An index row for `derived/topak-assessment-2026.10.03.md`, which two manifests measure and no row names.
- `mechanism/scripts/smoke.py`'s read of a key the grant reply no longer has (J-3; the format inventory's finding 19, open
  since 2026.10.03).
- The two tags the living documents name and the origin does not have (L-5).
- A row for `Workflow` and `Mesh` in the deadlock audit.
- ADR-0068's first revision: the sentence that says no module is written, and "would prove" (I1-1, I2-6).

---

## 6. What not to do yet

- **Do not draft another record.** Thirteen in five days is what this review is about.
- **Do not revise the overlay again before item 3.** Two revisions in a day left ADR-0068 behind and the floor
  stage behind the first of them.
- **Do not regenerate the diagrams to fix the four that changed** until the records they read are settled; a
  regeneration is a regression test, and its diffs are findings.
- **Do not rebuild the specification graph before the cut.** Its staleness is evidence of what the cut must
  measure.
- **Do not treat this review as the review.** It is the drafter's. ADR-0029 A2's reader has not been engaged.

---

## Sources

The four documents named at the head and their annex, `derived/topak-self-review-annex-2026.11.11/`;
`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` §7; the ratification-condition and Open-obligations
sections of ADR-0035, ADR-0036, ADR-0051 and ADR-0054 to ADR-0068 at `bbda621`;
`derived/topak-gaps-prioritization-2026.09.28.md` (`1a4fa6245267f039`), for form.

**What this does not claim.** That the sizes are estimates anyone but the drafter has checked. That the order is
the only defensible one. That anything in it has been started.
