# TOPAK — A PBFT sketch: what would have to change for the replicas to leave the trust-root class

**2026.11.07** · derived · a sketch, not a record · prepared by Claude at the custodian's request · read against
Genesis Checkpoint G11 (`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`), Theory of Operation revision 15
(`narrative/theory-of-operation.md`), ADR-0033 §3 and §4, ADR-0045 §2, §6 and Annex B, and the reference at the
tree after `9749dfa` (`mechanism/crates/topak-paxos`, `topak-node`). **Nothing here is built, drafted as a record or
decided.** §8 lists what a record would have to move; none is written.

**The question.** If the control plane's consensus were Practical Byzantine Fault Tolerance (Castro and Liskov,
1999) in place of crash-fault Multi-Paxos, which components would run it, which would have to change for it to buy
anything, which are untouched, and what would the corpus's own records have to say.

**The short answer.** Five components would run PBFT and six more would have to change before PBFT closed anything.
The protocol itself is the smaller half. PBFT makes replicas agree on *order*; it says nothing about *content*. The
forged admit the corpus names as the residual (residual-risk §1.7) is a content failure: one replica proposes an
`Admit` no floor evaluated, and under PBFT 2f honest replicas would order it faithfully. The residual does not move
until every replica can validate a proposal's content before it prepares it, and that validation work is the bulk
of the cost. A deployment that wanted Byzantine replicas should do that work first, under crash-fault Paxos, where
it already narrows the residual; the protocol change is what lets the row leave the trust-root class afterwards.

---

## 1. Where the corpus stands

The replicas are crash-recovery: a replica may stop, lose volatile state and restart from durable acceptor state,
and it does not lie (ADR-0033 §3). ADR-0045 makes the replica set a **trust root** (T-0045-1), with the forged admit
as the residual and mutual authentication as a delegated mitigation, still unbuilt (G5). ADR-0045 §6 weighed
"Require BFT consensus so that replicas become delegated" and did not take it: "weeks of work (09.28 estimate) to
move one row's class; the residual is stated instead". The 09.28 prioritization said the same
(`derived/topak-gaps-prioritization-2026.09.28.md`, G5 and item 23), and the effort estimate put the record at two
to three days and the consensus itself at weeks (`derived/topak-effort-estimate-2026.09.28.md`, item 23).

The position is restated in ToO §12 item 9 and §13 A9, residual-risk §1.7, the design-gap assessment row 4.1,
feature F2.62 and F8.9.4 of the 11.05 list, `mechanism/GAPS-AND-ASSUMPTIONS.md` I1 and G5, and the Adopter's Guide
rows 7 and a. A PBFT record reverses a stated position, so ADR-0029 §4's **C3** applies to it, and it touches
ADR-0033 §3 (the fault model), ADR-0033 §4 (the effect "only on the deciding replica"), ADR-0045 §6 and Annex B,
and ADR-0015's pointer to §4.

The 11.05 lattice note already separates the two quorums this sketch must keep apart: the **grant quorum** is an
authorization count over people, an axis of the deployment; the **consensus quorum** is an intersection condition
inside T-0045-1 (`derived/topak-safety-liveness-quorum-lattice-2026.11.05.md` §1). PBFT changes the second and
not the first.

## 2. The design point: order is not content

Under crash-fault Paxos the reference runs the admit path on one replica, the **deciding replica**: session, local
expiry, epoch fence, lease and alphabet, the lift, the floor, the bundle, then `Admit` is proposed and, after
commit, every replica re-runs the deterministic mechanism checks at the entry's log position (ADR-0033 §4;
`mechanism.rs` steps 1 to 7). **The floor and the bundle are not re-run at apply.** Their decision is recorded with
the digest of the frozen input it covers (ADR-0030 §4), and the apply-time re-check catches an admit that went
*stale* between decision and commit, not one that was *forged* at decision.

That split is what the residual rests on. Under PBFT it is unchanged unless the design changes with it. A Byzantine
primary pre-prepares `Admit { rec }` with a `rec` whose `floor_permit` field says permit and whose digest names a
frozen input nobody evaluated. Honest replicas, as the protocol stands, check the message's authenticity and
sequence and prepare it. The log then holds a well-ordered forgery. PBFT's client-side guarantee, f+1 matching
replies, does not help either: the replies report what was *applied*, and all 3f+1 replicas apply the same forged
entry.

So the requirement PBFT imposes on the mechanism is: **a non-faulty replica prepares a proposal only after
recomputing, from state it holds and evidence it can verify, that the proposal is one it would itself have made.**
Every seam where the reference today lets one replica compute and the others take must become either a
deterministic replicated computation or signed evidence from an identity the rules issue. §4 lists those seams.
The pattern already exists in the reference once: the operator's `Control` entry carries the request, the signature
and the thirteen facts, and every replica verifies the signature, recomputes the facts and refuses the entry if
they differ (I47, `State::control_facts`). That is the shape every entry kind would need.

## 3. Components that would run PBFT

| # | Component | Today | Under PBFT |
|---|---|---|---|
| 1 | **`topak-paxos`** | Sans-IO Multi-Paxos: `Prepare`, `Promise`, `Nack`, `Accept`, `Accepted`, `Commit`, `Heartbeat`, `CatchUp`, `Forward`; one replica plays acceptor, learner and, when elected, proposer; a `Voting` ghost checks `OneValuePerBallot` and chosen-uniqueness in the simulation | A PBFT core with the same `handle(Input) -> Vec<Output>` shape: `Request`, `PrePrepare`, `Prepare`, `Commit`, `Checkpoint`, `ViewChange`, `NewView`, `Reply`. n = 3f+1; a prepared certificate is 2f `Prepare`s matching a `PrePrepare`; a committed certificate is 2f+1 `Commit`s. The `Voting` ghost stays, as the cheat sheet prescribes: specify the crash-fault protocol, then the Byzantine one as a refinement where faulty acceptors are havoc over the message set (`derived/tlaplus-paxos-cheat-sheet-2026.09.13.md` §8) |
| 2 | **Durable state and the WAL** | `Durable<V>` is `promised` and `accepted`; the driver fsyncs `PersistPromise` and `PersistAccept` before any `Send`; the log is replayed from slot 1 and there are no snapshots (architecture description §5.3) | `Durable` gains the view, the prepared and committed certificates per sequence number, and the last **stable checkpoint**, 2f+1 signed `Checkpoint` messages over a state digest. ADR-0045 §6 classed compaction and snapshots as "service engineering, with no premise to declare". Under PBFT a checkpoint is protocol state: view change carries the last stable checkpoint and every prepared certificate above it, and a replica cannot discard below it. The row changes from none to inside the verified object |
| 3 | **Replica identity and message authentication** | None: three replicas in one process tree, TCP between them, unauthenticated; "anyone reaching a socket is a replica" (G5; Adopter's Guide row 7). G5's plan is mutual TLS | Every protocol message signed under a per-replica Ed25519 key (`authentic.rs` is the primitive, I7). The key set is the replica set's identity: either in the release's parameter set (I21, a promoted artifact) or in the issued rules under ADR-0025 §1 (f). Channel authentication is not sufficient: a `ViewChange` carries other replicas' `Prepare`s and `Checkpoint`s as evidence, and a `NewView` carries 2f+1 `ViewChange`s, so a message must be verifiable by a replica that did not receive it on a channel. mTLS may stay for confidentiality; it stops being the authentication |
| 4 | **The driver and the network** | `Forward` to the leader; heartbeat and election timeout on the host clock; `TcpNet` and `ChannelNet` point-to-point | All-to-all broadcast of `Prepare` and `Commit`, O(n²) messages per sequence number; a view-change timer in place of the election timeout, started when a request is received and cancelled when it executes; a client that times out broadcasts its request to every replica, which forward it to the primary and start the timer. The driver's ordering contract is unchanged in kind: persist, then send, then deliver. ADR-0032 §1 holds: the timers buy liveness, nothing in the safety argument reads them |
| 5 | **The formal layer** | No consensus module in `spec/`. The `Voting` abstraction exists only as the crate's ghost and in the cheat sheet. ToO §15 item 9 names "the drafted `Paxos` module" as owing proposer retry; it is not in the tree | New: `Voting.tla` (unchanged by the fault model), `Paxos.tla` (message level, crash-fault), and `BPaxos.tla` as a refinement with `CONSTANT FakeAcceptor`, `FakeSend` as havoc, and the abstraction function mapping faulty behaviour onto legal behaviour. TLC at n = 4, f = 1, two slots, per the cheat sheet's cost rule. For the reference, a `Mutation` set beyond the two crash-fault ones: an equivocating `PrePrepare` (two values, one sequence number), a forged `Commit`, a withheld `Prepare` set that stalls one sequence number, a `ViewChange` that omits a prepared certificate. Each must be caught by the simulation's invariants, or the invariants are vacuous (the corpus's mutation discipline, ADR-0046) |

## 4. Components that must change for PBFT to buy anything

| # | Seam | Today | What PBFT requires |
|---|---|---|---|
| 6 | **The decide step** (`mechanism.rs` `admit`) | The deciding replica runs the floor and the bundle once; `AdmitRecord` carries the outcome and the frozen input's digest; apply re-checks epoch, lease, rules epoch and round bound only (ADR-0033 §4) | Every replica re-runs the **floor** on the frozen input before it prepares the `PrePrepare`. Cedar is deterministic, linked in process and pinned by digest (`topak-floor`), so this is feasible as written, at the cost of one evaluation per replica per admit. The **bundle tier** is not deterministic across replicas: a sidecar's reachability and revision differ by host, and the WASM fallback decides only when it holds exactly the lease's revision (I2, ADR-0030 R4). Three designs, none chosen here: (a) a bundle evaluator with its own issued key, whose signed verdict over the frozen input's digest rides in the entry and is verified by every replica (a new trust-root row, with the same residual the Cedar engine's faithfulness carries); (b) 2f+1 replicas each evaluate the bundle and attest, and the entry carries the attestations; (c) the bundle is evaluated by the local WASM only, which makes it deterministic and retires the sidecar from the admit path, against I2's reason for keeping it. Option (a) keeps the sidecar; (c) is the smallest change; (b) costs the most and trusts the least |
| 7 | **Every "deciding replica computes, others take" seam** | The label facts of a `Consult` or `Actuate` are one replica's computation, which the others fold at apply and re-check only as far as `clearSet` (I46; G10 item 93; ToO §12 item 18). The `Activate` envelope is "what the deciding replica computed the seat may call". `WorkflowLoad`'s `outward` set is "what the deciding replica read from the bundle". A handle resolves from results one replica holds in memory (residual-risk §1.7). The appraisal at grant is one replica's, and every replica checks the verifier's signature and the nonce's epoch at apply (ToO §2.6) | Each becomes one of two things. **Recompute and refuse**: the entry carries the computed facts, every replica recomputes them from the revision and the round's state and refuses the entry if they differ, as `Control` already does. Label facts and the `Activate` envelope are recomputable from the entry of the lease's revision, which every replica holds. **Signed evidence**: the appraisal already is one, since the verifier is a trust root with an issued key (ADR-0034 §2), and needs no change. The `outward` set is read from the bundle, so it follows whichever bundle design item 6 takes. Handles are the hard case: a result one replica holds in memory is not replicated state, so either the result's digest is in the admit record and the handle resolves against it, or handles resolve only on the replica that holds the result and that replica's identity is in the entry |
| 8 | **Effect execution and emission** | The effect runs only after commit, only on the deciding replica (ADR-0033 §4): the tool host runs there, and the Kafka record is written there with the admit's index, fence, sequence and digest | Under PBFT the deciding replica may be the faulty one. Not performing the effect is safe: absence of effect is not an event (ADR-0015). Performing a *different* effect than the admitted one is not, and a tool invocation cannot run on 3f+1 replicas. The honest design gates the effect on the certificate: the **tool host** and the **emitter** perform an effect only on presentation of a committed certificate (2f+1 signed `Commit`s) for that admit at that sequence number, check the action against the admitted record's digest, and the emitted record carries the certificate. The tool host and the emitter then verify and do not trust, which is the move ADR-0045 §2 asks for. For a `Report`, the Observer reads the certificate on the topic (item 11). For an `Actuate`, the downstream system is as trusted as it was: ADR-0056's position stands |
| 9 | **The clients: `topak-mcp`, the operator CLI, the launcher bridge** | Each speaks to one replica over a Unix socket (`api.rs` `serve_agents`, `serve_operator`); `topak-contain`'s bridge is the session at rung 1 | Each client knows the replica set and keys, sends to the primary, broadcasts on timeout, and accepts a reply only when **f+1 replicas** return the same result. A denial is not ordered (ADR-0015), so a denial from one replica remains one replica's word; a client that wants a denial it can rely on asks f+1. The MCP front door's tool list (ToO §2.10, ADR-0048) is derived from replicated state and is fine; the per-call result is what needs f+1 |
| 10 | **Session tokens** (I14) | A bearer token minted at random by the granting replica, held in that replica's memory, not replicated; it carries (seat, lease, epoch) into every action | A Byzantine replica mints seats. The token must be derivable from the log or verifiable by any replica: for instance the lease's fence and epoch signed under a key the grant records, checked by whichever replica receives the action. Rung 2 and 3 attested sessions already bind every action to the guest's session key, which the lease records and every replica checks at decide and at apply (I41), and survive unchanged. Rung 1's bearer token does not |
| 11 | **Observers and the correlator** | Cell Observers and the correlator read round topics written by the deciding replica (ADR-0038, ADR-0043); heartbeats are admits on the log; Observers combine by any-of and have no quorum (ToO §5.1) | A reader that trusts a topic written by one replica trusts that replica. Under PBFT the reader verifies the committed certificate on each record (item 8), or reads from f+1 replicas and takes agreement. The any-of combination, the absence of an Observer quorum and the heartbeat coupling (ADR-0039) are unaffected: they are about what an Observer may do, not about what it reads |

## 5. Components that do not need PBFT

- **The floor and bundle policy text**, the schema and the gates (`floor/`, `policies/`): what is evaluated, not who evaluates it. Item 6 changes where evaluation happens, not what it says.
- **The lift** and the alphabet (ADR-0022, ADR-0040): syntactic, deterministic, already run wherever the admit is decided.
- **Denials** (ADR-0015, ADR-0020): unordered and local by design. Item 9 notes what a client must do to rely on one.
- **Observer combination** (ADR-0038): any-of, no quorum, by design; `Observers.tla`'s `M_QUORUM` is the mutation that shows why.
- **Grant quorums** (ADR-0024, ADR-0050, ADR-0052): authorization counts over people on an issued roster; a separate axis (lattice note §1).
- **Kafka** (ADR-0005): neither the ordering authority nor the system of record; its records gain a certificate (item 8) and its role does not change.
- **The archive** (T-0045-7, delegated): its failure loses evidence and never authority.
- **The verifier** (ADR-0034 §2) and the **anchor** (ADR-0025): trust roots with issued keys, already the shape item 7 wants.

## 6. Scale

| | Today | Under PBFT |
|---|---|---|
| Replicas | 3, one process tree, tolerates one crash | 3f+1 = 4 at f = 1, across fault domains, or nothing is tolerated that was not tolerated before |
| Messages per committed entry | O(n): `Accept` and `Accepted` | O(n²): `Prepare` and `Commit` all-to-all, plus signatures to verify |
| Floor evaluations per admit | 1 | n, or 2f+1 if a replica may prepare on others' attestations (not sketched here; it weakens item 6's guarantee) |
| State the protocol must keep | Promise and accepted per slot | Certificates per sequence number, stable checkpoints, view-change evidence |
| Spec modules | 0 consensus modules in `spec/` | 3 (`Voting`, `Paxos`, `BPaxos`) and a Byzantine mutation set for `sim.rs` |
| Wall clock per admit | one round trip to a quorum | three message delays in the common case, plus n floor evaluations |

The 09.28 estimate of "weeks" for item 23 was for the protocol alone (§3). Items 6 to 11 were not estimated then and
are not estimated here, beyond the observation that item 6 is a design decision with three options and items 8 and
9 change every client and both effect paths.

## 7. Staging, if it were taken on

0. **Records.** The reversal (§8). Nothing else should move until the position is restated, because the corpus
   cites the current one in eleven places (§1).
1. **Determinize decide.** Make every entry kind recomputable or evidence-carrying (item 7), choose a bundle design
   (item 6), and make apply re-run the floor. This is worth doing **under crash-fault Paxos**: it turns the
   apply-time re-check from "stale only" into "stale or forged by a replica that did not run the floor", and it
   narrows T-0045-1's residual without changing the protocol. It is also what every later stage depends on.
2. **Replica keys and signed messages** (item 3). Closes G5 by a stronger route than mTLS. Worth doing under
   crash-fault Paxos too: it is the authentication the Adopter's Guide row 7 already declares and the reference lacks.
3. **The PBFT core**, the durable state, the driver (items 1, 2, 4), with `BPaxos.tla` and the Byzantine mutations
   (item 5) in the same batch, by ADR-0046's rule that a mutation set accompanies every module.
4. **Certificate-gated effects and f+1 clients** (items 8 to 11). This is where T-0045-1 leaves the trust-root
   class: a single replica's failure can then only subtract, and the row becomes delegated up to f, with the replica
   set's identity still fixed by promotion.

Stages 1 and 2 stand on their own. Stages 3 and 4 only pay together.

## 8. What a record would have to move

| Where | Says now | Would say |
|---|---|---|
| ADR-0033 §3 | Crash-recovery, not Byzantine; a Byzantine replica is outside the model | The fault model is Byzantine up to f of 3f+1; a replica's identity is its key; what a faulty replica can and cannot do |
| ADR-0033 §4 | The effect runs only on the deciding replica; the floor and bundle are not re-run at apply | The effect runs on presentation of a committed certificate; the floor is re-run at prepare; the bundle per item 6's choice |
| ADR-0045 T-0045-1 | Trust root; residual: a forged admit | Delegated up to f, identity by promotion; residual: f+1 compromised replicas, or a compromised bundle evaluator under option (a) |
| ADR-0045 §6, options table | "Require BFT consensus … Not taken" | Taken, with the reason the 09.28 estimate's premise no longer holds, or whatever the reason is |
| ADR-0015 (pointer) | Points to ADR-0033 §4 | Follows it |
| ToO §12 item 9, §13 A9 | The replicas are trusted | The replicas are checked up to f |
| `GAPS-AND-ASSUMPTIONS.md` I1, I14, G5 | Crash-fault; bearer token; no replica authentication | Each per items 1, 10 and 3 |
| Adopter's Guide rows 7 and a | Declaration: crash-fault, mutually authenticated | Declaration: n, f, the key set, the bundle design |
| Residual-risk §1.7 | A compromised replica forges admits | Retired, or restated as f+1 |
| Design-gap assessment 4.1; feature list F2.62, F8.9.4 | BFT considered and declined | Superseded by the record |

A record that did this would carry **C3** (a reversal) and, for the certificate-gated effect path, **C2**
(exhaustiveness of the paths an effect may take, ADR-0015). It would be ratified by one person and await the first
post-bootstrap quorum like the twenty-nine before it (ToO A8).

## 9. What this sketch does not say

- Whether to do it. ADR-0045 §6's reason for not doing it, that it moves one row's class at weeks of cost, is still
  true of stage 3 alone; §7 argues that stages 1 and 2 are worth doing regardless and that the question is whether
  stages 3 and 4 are.
- Which BFT protocol. PBFT was asked for. A linear protocol (HotStuff and its descendants) changes items 1, 2 and 4
  and nothing in items 6 to 11, which is one more reason the second table is the one that matters.
- Any number. n, f, the key custody, the bundle design and the fault domains are a deployment's to declare under
  ADR-0058, not this sketch's.
