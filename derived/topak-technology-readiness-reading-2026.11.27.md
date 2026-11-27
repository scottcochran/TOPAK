# TOPAK on NASA's technology readiness scale: TRL 3 as a whole, the admit path at TRL 4

> what are NASA's technology readiness levels?

> where does TOPAK rank

> look in the branches

> write that up as a derived doc

(The custodian's prompts of 2026.11.27, in order. The first three were answered in the session, and this document
is the fourth.)

**2026.11.27** · derived · a reading, not a record · prepared by Claude at the custodian's request · basis: the tree
at `231ca68` (`main` after pull request #109), with `README.md`, `mechanism/README.md`,
`mechanism/GAPS-AND-ASSUMPTIONS.md`, Genesis Checkpoint G12's reference row
(`checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md`) and
[`topak-shortest-path-to-poc-2026.11.26.md`](topak-shortest-path-to-poc-2026.11.26.md); and the twenty-six remote
branches other than `main`, as fetched on 2026.11.27, four of them read (§4) · NASA's scale from the agency's web
article "Technology Readiness Levels", read through a fetch agent on 2026.11.27 and not held in the tree · **nothing
was run**: every test count, trace count and fault run below is the corpus's own report, cited where it is made

Nothing here is ratified, and this document proposes no decision text. The corpus does not rate itself on this
scale, on `main` or on any branch, so the level is this document's reading and nobody's finding. Each lead in §7 is
for the custodian, and no entry is made.

---

## 0. Verdict

1. **TOPAK as a whole is at TRL 3.** The concept is formulated and its critical function has analytical and
   experimental proof of concept. It is not at TRL 4 as a system, because most of the system has never been
   built, let alone integrated. §3.
2. **The admit path alone is at TRL 4.** Its components have run together in a laboratory setting: three
   replicas, consensus, the Cedar floor, the bundle tier and an MCP client. §3.
3. **The branches do not change either level.** One unmerged branch makes the admit path's TRL 4 firmer, with a
   containerised cluster, real Kafka and a sidecar, a leader crash and a partition. No branch builds a missing
   component. §4.
4. **The scale does not count what the corpus is strongest at.** It rates how realistic the test environment
   was. Model checking, proofs and a second derivation in Lean add confidence at a level and do not raise it. §5.
5. **Four statements of the session's answers are corrected here.** §6.

---

## 1. The scale

The nine levels, in the short form the session gave. This form was written from general knowledge and was not
checked against a NASA document; the agency's procedural requirement that defines the levels (NPR 7123.1) was not
read.

| TRL | Short form |
|---|---|
| 1 | Basic principles observed and reported |
| 2 | Technology concept or application formulated |
| 3 | Analytical and experimental proof of concept of the critical function |
| 4 | Component or breadboard validation in a laboratory environment |
| 5 | Component or breadboard validation in a relevant environment |
| 6 | System or subsystem model or prototype demonstrated in a relevant environment |
| 7 | System prototype demonstrated in an operational environment |
| 8 | Actual system completed and qualified through test and demonstration |
| 9 | Actual system proven through successful operation |

NASA's web article states the levels in prose, and its wording agrees with the table at the three levels this
reading turns on. At TRL 3, "Often during TRL 3, a proof-of-concept model is constructed." At TRL 4, "multiple
component pieces are tested with one another." At TRL 5, "Simulations should be run in environments that are as
close to realistic as possible."

---

## 2. How the scale was applied to a pattern

TOPAK is an architecture pattern with a reference implementation of one part. The scale was written for hardware
that flies. Three choices were made to apply it, and a reader who makes them differently will get a different
level.

- **What is rated.** The mechanism the records hand to an implementation, and not the design corpus as a document.
  A specification can be complete and ratified and still be at TRL 2.
- **What counts as a component.** A part of that mechanism with code and a test that exercises it, which is the
  meaning the unmerged plan of §4.4 gives to *built*.
- **What counts as a relevant environment.** Agents doing real work against the mechanism, some of them trying to
  defeat it, under a deployment's own declared values. The archetype values, a scripted client and a scripted
  occupant are a laboratory.

---

## 3. The reading on `main`

### 3.1 Past TRL 2

The concept and its application are formulated in records, of which a large part is ratified, and in a narrative
at revision 16 with a state of record at G12 (`README.md`).

### 3.2 At TRL 3, for the whole

The critical function is the admit decision, `admit ⟺ floor_permit ∧ ¬bundle_deny`, ordered by consensus and
re-checked at apply (`mechanism/README.md`).

- **Analytical.** The TLA+ modules are checked by TLC, proved in TLAPS and derived a second time in Lean
  (`README.md`, *Running things*).
- **Experimental.** G12's reference row reports 155 tests across fifteen binaries, none failing, run 2026.11.16,
  with the Rego tests and trace validation not rerun for that cut. The last trace validation on `main` replays 82
  traces and 1,007 steps through `spec/Mechanism.tla` (`spec/Mechanism-trace-results-2026.10.05.txt`).

### 3.3 At TRL 4, for the admit path

The admit path's components have been run together.

- The register's evidence row records a live smoke run on 2026.09.24 and 2026.09.25: three processes over TCP,
  real Kafka, a real OPA sidecar and an MCP client over stdio (`mechanism/GAPS-AND-ASSUMPTIONS.md` §1).
- The POC document records the smoke run repeated on 2026.11.26 at `ffd02f1`, in memory, with no Kafka and no
  sidecar (its L-1).
- The launcher has a real container round at rung 1, run when `TOPAK_DOCKER_IMAGE` is set
  (`mechanism/GAPS-AND-ASSUMPTIONS.md` §1).

### 3.4 Not TRL 4, for the whole

- **Components never built.** The register's scope line excludes the Observer and correlator, the archive and
  plaintext store, write-time masking, the anchor ceremony and bootstrap, confinement and erasure execution.
- **Confinement is real at one rung.** Rung 1 is real, rung 3 is SIMULATED behind a feature, and the register's
  table of records says of ADR-0022 §6 that nothing is enforced and every lease is rung 0.
- **The floor linked is not the floor in force.** `topak-floor` compiles in `floor/proposed/workflow-floor.cedar`
  (`mechanism/README.md`, crate table).
- **Some of what is built follows records that are Proposed or await confirmation.** The register's §1.1 lists
  them by status.
- **The values are the archetype's.** `mechanism/README.md` says the reference "runs the archetype values and
  nobody ships the archetype."

---

## 4. What the branches add

Twenty-six remote branches other than `main` were listed against it. None states a readiness level.

| Kind | Count | Branches |
|---|---|---|
| Derived documents only | 16 | The sixteen whose changes fall under `derived/` alone |
| Reference or specification work | 3 | `compose-stage-a`, `claude/loving-gauss-3q99gi`, `claude/exciting-darwin-gkqg58` |
| Other single-purpose changes | 4 | `reviewers-guide-2026.11.20` (the guide), `underground` (a diagram), `ccr-36056197-ggxmhm` (a revision of ADR-0036, Proposed), `ccr-ba6223ea-vsdwd5` (CI and rulesets) |
| No net change against `main` | 1 | `claude/vigilant-lovelace-memrqa` |
| No common history with `main` | 2 | `ccr-5bee41f9-96r6ep`, `claude/topak-nvidia-agent-safety-nz0om8`; not read |

Four were read for this document: the three in the second row, and one of the sixteen, the plan of §4.4. The
other fifteen derived documents were not read, and one of them may bear on this reading.

### 4.1 `compose-stage-a` at `c66f300` (2026.11.26)

One commit on `8b3b95b`. It adds `mechanism/Dockerfile`, `mechanism/compose.cluster.yml` and
`mechanism/scripts/faults.sh`, and a derived document, `topak-poc-containers-before-kubernetes-2026.11.26.md`.

- Three replicas run in three containers with real TCP between them, Kafka and an OPA sidecar, every image pinned
  by digest.
- The commit message reports the cluster smoke run made twice, with the round topics in Kafka and the bundle
  queries at the sidecar.
- `faults.sh` kills the leader and restarts it, then partitions the leader and heals it. The derived document's
  verdict reports that the survivors kept ordering, the restarted replica caught up, and the partitioned replica
  converged once reconnected.
- The same document says "A cluster on one Docker host is a demonstration and not a deployment." The commit
  message says `cargo test` was not run.

This is the strongest TRL 4 evidence for the admit path anywhere in the repository. It is a laboratory run: the
client is `smoke.py`, the faults are the two the script injects, and the replicas are crash-fault.

### 4.2 `claude/loving-gauss-3q99gi` at `c7beda0` (2026.11.21)

Eleven commits on `ffd02f1`. `spec/Mechanism.tla` is extended to workflows and meshes, and trace validation is
reported at 106 traces and 1,716 steps, every step matching (`spec/Mechanism-trace-results-2026.11.21.txt` on that
branch). A first cut of `MechanismFree.tla` runs the model freely over a generator of entries. This widens the
analytical half of TRL 3 to the workflow engine.

### 4.3 `claude/exciting-darwin-gkqg58` at `dfffe83` (2026.11.12)

One commit on `dbb2b0c`. It bounds the Wasm tool host's memory, host allocations, connections and wall clock, with
four tests. It hardens a built component and changes no level.

### 4.4 `ccr-c017f01f-gvby82` at `d59a6c4` (2026.11.07)

One commit on `9749dfa`, adding `topak-complete-reference-mechanism-plan-2026.11.07.md`, read against G11. Its
count is the closest thing in the repository to a denominator for this reading:

- Forty-seven components in six layers. Sixteen exist, four of them partial in a way the plan says matters.
  Thirty-one are missing or stood in for by a register assumption.
- Three missing components gate most of the rest: a read path on the transport, the Observer as a principal, and
  promotion as a pipeline. The plan says of the last that "no first lease has ever come from a quorum."

The plan is unmerged and three weeks older than `main`. Its count was not re-taken here, and ten records
(ADR-0059 to ADR-0068) have been drafted or ratified since its basis.

---

## 5. What the scale does not see

A level on this scale is set by where the thing was exercised: on paper, on a bench, in a relevant environment, in
operation. It has no place for how strong the argument is at a level. So a design whose admit decision is proved,
derived twice and replayed step for step against its model sits at the same level as one whose proof of concept is
a script that ran once.

Read the other way, the scale is fair to the corpus. `README.md` says the corpus "is not a deployable system", and
TRL 3 with one subsystem at TRL 4 says the same thing in another vocabulary.

The step to TRL 5 is the step §2 defines: the integrated components exercised by real agent workloads, with
adversarial behaviour, under values a deployment declared. Nothing in the tree or on a branch attempts it. The
step to TRL 4 for the whole is the plan of §4.4, or one like it, carried out.

---

## 6. Corrections to the session's answers

- **C-1. The branch count.** The session said twenty-eight remote branches besides `main`. There are twenty-six.
- **C-2. The live run.** The session's first answer said, from the register, that the live smoke run had not been
  repeated since 2026.09.25, and its second said `compose-stage-a` answered that. `main` already recorded a repeat
  on 2026.11.26, in memory, in the POC document's L-1. What `compose-stage-a` adds is the repeat with real Kafka
  and the sidecar, which the POC document's L-3 says was not run.
- **C-3. "The tests pass."** The session said the mutation and end-to-end tests pass. It ran none. G12's
  reference row reports the run of 2026.11.16, and that is the basis.
- **C-4. Two statements about the scale.** The session said TRL 6 is the usual threshold at a flight project's
  preliminary design review, and gave a history of the scale. Neither was checked. The NASA article read for this
  document says nothing about a design review.

The session also said "about a third of the mechanism is built". That is sixteen of forty-seven, by a plan that
§4.4 says is unmerged and was not re-counted.

---

## 7. Leads for the custodian

- **L-1.** The register's evidence row still says the live smoke run has not been repeated since 2026.09.25. The
  POC document's L-1 raised this on 2026.11.26. If `compose-stage-a` merges, the row is two runs behind.
- **L-2.** Whether the corpus should state a readiness level at all is the custodian's to say. If it should, the
  Adopter's Guide or the Reviewer's Guide is where a reader would look for it, and §2's three choices would need
  to be the custodian's own.
- **L-3.** The plan of §4.4 is the only inventory of the whole mechanism and it is unmerged, against G11. A
  re-count against G12 would give this reading, and any later one, a current denominator.
- **L-4.** NASA publishes software descriptions and exit criteria for each level in NPR 7123.1. A reading against
  those, and not against the short form of §1, would be the stricter one.
