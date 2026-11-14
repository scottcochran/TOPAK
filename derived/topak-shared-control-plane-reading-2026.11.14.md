# A shared control plane fails together: an outage analysis read against TOPAK

**2026.11.14** · derived · a reading, not a record · basis: the tree at commit `bb76b46` (Genesis Checkpoint G11;
Theory of Operation revision 15; sixty-eight record files; `mechanism/`), and a Gemini conversation the custodian
supplied, *Analyzing the ATC Router Outage* (created 2026.11.13) · three suggested entries for the open-findings
register, none made · nothing was changed in the tree but this file and its index row · prepared by the assistant
at the custodian's request

Nothing here is ratified, and this document proposes no decision text. Each entry says what the tree holds, what it
does not, and what kinds of answer exist; choosing among them is a record's work.

**Not independent.** The reader is the same kind of model as the drafter of the corpus. The three entries came from
reading an outside text against the tree, which is a different prompt and not a different reader.

**The source is used as an argument, not as evidence.** The conversation is a language model's account of press
reports of an outage of 2026.11.13, with no post-mortem published. The PDF print the custodian supplied clips the
end of each answer. Nothing below depends on whether the account of the outage is right: the entries stand or fall
on the lines of the tree they cite.

---

## 1. The argument in the source

The network in the account had physical redundancy and logical compartments, and failed nationwide from one update
at one node. The account gives five reasons, and they are general:

| # | The source's claim | In one line |
|---|---|---|
| S1 | Logical compartments shared one routing control plane | Separation above a shared substrate is not a failure domain |
| S2 | Control, data and administration travelled in-band on the same queues and processors | Load on one starves the others, and the operator loses the channel a rollback needs |
| S3 | An update was pushed with no staging and no boundary it could not cross | The management plane is the vector that bypasses every compartment |
| S4 | Redundancy propagated the fault, and bringing every site back at once risked a second collapse | Recovery is a load, and the largest one |
| S5 | The backups could empty the sky and could not run it | A safe stop is not service |

## 2. Where the corpus already holds the position

Kept short, because none of it is new.

- **S1, in part.** Ordering lives in the consensus log and the transport orders nothing (ADR-0005), so a payload flood
  cannot move the causal frame. A bundle can only narrow (ADR-0030), so a bad bundle cannot spread as authority. A dead
  Observer stops its own Thinker and nothing else, and the correlator is never coupled, to avoid "the fleet-wide stall
  ADR-0038 exists to avoid" (ToO §5.4).
- **S2, for safety.** Authority ends without the log: lease expiry and the passive e-stop run on a local clock whose
  error ends the lease early (ADR-0032 §2). The genesis floor is resident and fetched from nowhere (ADR-0012,
  ADR-0027).
- **S5, declared.** "The corpus's answer to failure is to stall" (ToO §5.5), and item 21 of ToO §12 says no stall is
  shown to end. A-0068-4 says a stall is not safe for a body in motion, for the overlay only.

What remains is S2 for liveness, S3 and S4. Each is an entry below.

## 3. Suggested entries

In the register's columns. **At the pin** is graded at `bb76b46`. Severity is the drafter's.

| Id | Statement | Against | At the pin | Carried by |
|---|---|---|---|---|
| E1 | **Every kind of entry shares one path into the log, and no record orders one kind ahead of another.** An operator's fence, a revocation, an Observer's heartbeat and an emergency seat's call wait behind ordinary admits. `DenyAlwaysAvailable` says a deny is enabled; nothing says it is ordered within any bound | ADR-0039 §6; ADR-0050 §4; ADR-0032 §4; `mechanism/crates/topak-node/src/lib.rs` | **open** | nowhere |
| E2 | **A mechanism release has no rollout.** Promotion ends at publication, and the only fleet-wide instrument is the epoch fence, which is all at once. No record says in what order replicas take a release, whether two releases may decide in one log, or how a release is taken back. Reverting a tightening of the floor is a relaxation, so the way back needs the anchor | ADR-0069 §8; ADR-0031 §4, §5; ADR-0024 §1; ADR-0033 §4; `mechanism/GAPS-AND-ASSUMPTIONS.md` I21 | **open** | nowhere |
| E3 | **Recovery from a fleet fence is unordered and unpaced.** Every lease ends at once, Observers' and operators' included. The grants that follow have a forced order the records imply and none states, each is a log entry with an attestation, and nothing bounds how many are asked for at once | ADR-0031 §5; ADR-0050 §10; ADR-0039 §2; ADR-0034 §3 | **partly addressed** | ADR-0050 Open obligations (the operators' first leases only); liveness plan Tier 1 items 2 and 3 (unmodelled) |

### E1. One path into the log · Medium

**What the tree holds.**

- "Heartbeats are admits, one per `T_obs` per Observer, on the consensus log" (`decisions/ADR-0039.md`, §6,
  Throughput). The record states it as a cost and gives it no bound.
- An operator's six control actions are signed requests decided on the floor and ordered like any entry (ADR-0050
  §4; `mechanism/GAPS-AND-ASSUMPTIONS.md` I47). A call under an emergency activation "is admitted by the ordinary
  permit" (`mechanism/crates/topak-node/src/mechanism.rs`, at the admit record).
- At the reference there is one queue. `propose` is the only way into the log, it has nine callers, and it feeds one
  channel of 1,024 entries with no class (`mechanism/crates/topak-node/src/lib.rs` line 85). A proposal not committed
  in five seconds returns an error (`COMMIT_DEADLINE`). So a fence under load is not delayed without limit: it fails.
- Three things bound the load a principal can add. The round bound `R` counts every admit, `Consult` included
  (ADR-0042 §2). A denial is not ordered (ADR-0015), so a refused request costs the deciding replica and not the
  log. Denials written after a seal stop at a limit (`after_topic_limit`).
- ADR-0050 names denial of service *by* an operator. No record names denial of service *of* one.

**What it does not hold.**

- A statement that an entry which subtracts authority is ordered ahead of one that adds it, or within any time.
  `DenyAlwaysAvailable` (`spec/Operators.tla`) is an invariant over `ENABLED`: the model has no queue, so an action
  enabled there may wait at the reference.
- A term for it in the timing budget. `W + L + D < T_irrev` has `W` as the propagation of an effect, "guaranteed by
  the mechanism" (ADR-0032 §4). The time between a person signing a stop and the log ordering it is in none of the
  three, on the drafter's reading.
- A capacity. Heartbeat load is the number of Observers over `T_obs`, and no document compares it with what the log
  orders per second. The loop the source describes has a form here: a heartbeat delayed past `T_obs` by a full queue
  makes its Observer stale, which stalls its Thinker (R3), and A18 has the Thinker ask again. The retries are denied
  at decide and do not reach the log, so the loop loads replicas and not the queue. Nobody has run it.

**What bounds the exposure today.** Local expiry: with the log unable to order a stop, every lease still ends
within its `ttl`, at most `T_persona`, an hour at the placeholder value. The entry is about that hour, and about an
emergency call that Tier 0 proves an Observer cannot block and that a queue still can.

**Kinds of answer.** Classes of entry with capacity reserved for the subtracting class and for heartbeats. A declared
log capacity and a heartbeat budget, as deployment values beside `T_obs` and `K`. A fourth term in the budget, or a
statement that `W` covers it and why. A stop that needs no log beyond expiry, which is a design question and the
only one of the four that is physically out-of-band in the source's sense.

### E2. No rollout for a mechanism release · Medium-High

**What the tree holds.**

- Mechanism releases are promoted, "including policy-floor and rules-floor changes" (`decisions/ADR-0024.md`, §1),
  and the policy floor ships inside the release (ToO §3.2).
- The pipeline ends: "Publishing locates; rollout ends rounds", and "a new revision reaches a live principal by
  ending its round, and across the fleet by an epoch fence" (`decisions/ADR-0069.md`, §8, restating ADR-0031 §4).
  The fast path for strictly subtractive bundles "stays deferred".
- For a **bundle** a narrower instrument exists and is not named as one: end one principal's round and grant again
  against the new revision (ADR-0031 §4). That is a rollout one principal at a time, by an operator's hand.
- For the **mechanism** the reference has one rule. Parameters "must match on every replica, and their digest is in
  every admit; `apply` rejects an admit decided under other parameters" (I21;
  `mechanism/crates/topak-core/src/state.rs`, `apply_admit`). The admit record also carries the digest of the floor
  it was decided under. Nothing compares that digest at apply, and ADR-0033 §3 says the apply-time checks "do not
  re-run the floor".

**What it does not hold.**

- How a promoted release reaches the replica set: one replica at a time or all, and who decides. The stages of
  ADR-0069 are keyed by digest up to publication and say nothing after it for this artifact class.
- What two releases in one log mean. As the code reads, each replica compares an admit with its *own* parameters. Two
  replicas holding different parameters would return different results for one log index. This is read from the
  source and was not run. For the floor there is no comparison at all: an admit decided under the old floor is
  applied by a replica linked to the new one, and the reverse.
- A canary. No record has a stage between "promoted" and "in force for every principal" in which a release decides
  for some and not for all, and no gate reads the result of such a stage.
- A way back. A release that tightens the floor is "an ordinary promotion". Taking it back is a relaxation, "an
  anchor issuance **and** a promotion" (ToO §3.2). The classification is computed, which is right, and it means the
  revert of a bad tightening takes the slowest authority path in the corpus, when the fleet is stalled by it. A
  floor too tight is safe and is the source's outage exactly: nothing unsafe was admitted, and nothing was.

**Why it ranks first of the three.** S3 is the source's root cause, and unanimity does not answer it. Reviewers who
all pass a release that then stalls every cell have failed together (ToO §12 item 2), and what limits the damage
after that is how far the release went before someone saw. Here it goes everywhere.

**Kinds of answer.** A stage after publication, in ADR-0069's terms, that takes a release to a declared subset and
produces signed evidence a later stage reads. A rule for two releases in one log: forbidden, with the cutover an
ordered entry at one index, or allowed, with the floor digest compared at apply as the parameter digest is. A
standing, pre-voted revert to the last release in force, so that going back to a floor already ratified is not a
fresh relaxation. Each touches accepted records and the last touches ADR-0026 and ADR-0030.

### E3. Recovery from a fleet fence · Medium

**What the tree holds.**

- "A fence storm is an availability event. Each epoch fence ends every live round" (`decisions/ADR-0031.md`,
  Consequences). "A fleet fence leaves nobody able to regrant. Recovery is a quorum's work. It is the safe direction
  and it is the slow one" (`decisions/ADR-0050.md`, Consequences).
- One open obligation: "Recovery after a fleet fence: whether a standing seating may re-grant its operators' first
  leases without a new tally, and what break-glass is for here" (ADR-0050, Open obligations). The 11.11 register
  grades ADR-0050's obligations partly addressed, under G11 items 88 and 90.
- A Thinker's next round "is granted only once a cell Observer has read its last round to the seal" (ToO §5.4;
  ADR-0039 §2). Every grant is appraised against a nonce drawn from the log (ADR-0034 §3).
- The liveness plan has the two premises a proof would need and neither is modelled: every ended lease eventually
  yields a seal, and "repeated fences can starve a promotion forever" (`derived/topak-liveness-2026.10.07.md`, Tier 1
  items 2 and 3).

**What it does not hold.**

- The order. After a fence the Observers' leases have ended with the rest, so on the drafter's reading recovery is
  forced into four steps: a quorum seats operators; operators grant Observers; each Observer reads its Thinker's
  ended round to the seal; only then is a Thinker's grant enabled. The records imply this and no record states it. A
  deployment that grants in another order is refused, correctly, and nothing tells it why in one place.
- A pace. Each step is a batch of log entries, each grant carries an attestation, and the Observers begin
  heartbeating as they are granted, on the one path of E1. Nothing bounds how many grants are asked for at once, and
  the proposal that waits more than five seconds fails and is asked again. This is the source's S4 in the corpus's
  terms: the largest load the log sees arrives when it has just been emptied.
- A seal for a fenced round. Coverage reads the seal, and the plan's item 3 says a seal that never lands "is a silent
  deadlock of the next round". A fence ends every round at once, so every cell depends on that unmodelled step
  together.
- A measure. No test at the reference fences a fleet of more than a few principals and times the way back, and the
  residual-risk statement of 2026.11.11 has no row for it.

**Kinds of answer.** The recovery order written down as a consequence of ADR-0031 §5, ADR-0039 §2 and ADR-0050,
which is narrative and needs no new decision. A declared regrant rate, or grants in waves by domain, as a deployment
value. The plan's item 3 modelled, with a fence as one of its three cases. A rehearsal at the reference: fence, then
time each of the four steps. The first and the last can be done without a record.

## 4. What was not made an entry

- **S1 at the replica set.** Cells, domains and planes are compartments over one replica set running one release.
  ADR-0045 already carries the replicas as a trust-root row with crash-recovery assumed (A9), and a common-mode fault
  in the release is E2's subject. A row for "one release, every replica" would restate both.
- **S5 outside the overlay.** That a stall is not service is ToO §12 item 21 and assumption A12's second column. An
  assumption of use that names the deployment's safe state, as A-0068-4 does for vehicles, would be a sentence in
  §13 and is the custodian's to want.

## What this does not claim

It does not claim the outage happened as the source says, or that the network in it resembles TOPAK: one is a
routed network and the other an authority tier, and the comparison is of failure shapes only. It does not claim any
of the three is a safety defect. In each, what fails is availability, in the direction the corpus chose. It does not
claim the reference's queue, deadline or parameter check are the mechanism's: ADR-0033 makes the reference evidence,
and the entries are against the records' silence, which the reference shows. Nothing was run for this document. The
one statement about replicas disagreeing is read from the source and marked so.

## Sources

- Gemini conversation, *Analyzing the ATC Router Outage*, created 2026.11.13 and published the same day, shared by
  the custodian at `https://share.gemini.google/TZ0gugx2y4je`, read from an eleven-page PDF print on 2026.11.14.
  Each answer is clipped at the page's end. The press reports it cites were not opened.
- The tree at `bb76b46`: `narrative/theory-of-operation.md` (§3.2, §5.4, §5.5, §10, §12, §13);
  `decisions/ADR-0005.md`, `decisions/ADR-0015.md`, `decisions/ADR-0024.md`, `decisions/ADR-0031.md`,
  `decisions/ADR-0032.md`, `decisions/ADR-0033.md`, `decisions/ADR-0034.md`, `decisions/ADR-0039.md`,
  `decisions/ADR-0042.md`, `decisions/ADR-0050.md`, `decisions/ADR-0069.md`;
  `mechanism/GAPS-AND-ASSUMPTIONS.md`; `mechanism/crates/topak-node/src/lib.rs`,
  `mechanism/crates/topak-node/src/mechanism.rs`, `mechanism/crates/topak-core/src/state.rs`; `spec/Operators.tla`;
  `derived/topak-liveness-2026.10.07.md`, `derived/topak-open-findings-register-2026.11.11.md`,
  `derived/topak-residual-risk-statement-2026.11.11.md`.
