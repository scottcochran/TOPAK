I'll look through the repo to find the gaps tracking and what TCB refers to.

I've read the state of record (G4 open list, the mechanism gaps register, the 09.28 effort estimate, ADR-0033/34/36 and the 09.25 review) and have what I need. Here is the assessment.

**Framing.** "Gaps" here means G4 §7's 34 open items plus the reference's G1 to G17. Effort figures are the 09.28 estimate's custodian-days. For part 3, I read "delegated to TCB" as: gaps better closed by naming a substrate component as a row in the TCB declaration record than by building them in TOPAK. The corpus already has the test for that in ADR-0034's context: delegate a mechanism whose failure can only subtract authority; anything whose failure could add authority stays TOPAK-authored and consensus-backed.

## 1. Highest ROI pending items

| Item | Cost | What it buys |
|---|---|---|
| Independent confirmation pass (ADR-0029 A2, CR-21) | 5–10 days of dispositions, plus a reviewer | The only item that moves all three external grades at once and is a bootstrap precondition. Zero effort has started; the blocker is recruiting, not work |
| ADR-0036 ratification run, then the node-side launcher and a P3-passing image (items 34–36, G1) | 1–2, 3–5, 2–4 days | Turns the largest gap from "nothing" into a rung-1 lease whose Mediated verdict is derived from a declared profile. The image and the design already exist |
| Run's alphabet record (item 13) | 3–5 days | Highest fan-out of any single record: unblocks the Run profile, ADR-0022 §6 for Run, G3, the Run half of the floor and three provisional code sites |
| TCB declaration record (item 16) | 2–3 days | Four separate debts (ADR-0030, 0033 §3, 0034 §6, 0036 §5) collapse into one record, and it is the precondition for every delegation in part 3 |
| Bundle signing (item 18, G7, CR-24) | 0.5–1 record, 1–2 code | Closes the named asymmetry: a corpus pinned to 28 digests trusting an unsigned tarball |
| The three missing bootstrap TLA+ modules | 3–5 days | With the review above, this is the entire bootstrap-eligible set |

Together the first, fourth and sixth rows are the whole critical path to bootstrap eligibility. The second and third rows are the path to a first `Contained` principal, though that also waits on ADR-0035's θ values, which no custodian effort can produce.

## 2. Easiest wins

Each is under a day or purely mechanical, and none waits on another decision.

- **ADR-0035 R3 for ADR-0036 finding 1** (item 32). Half a day. Two sentences settling whether the ingress bound covers the occupant's reads or the tool's.
- **Bundle signing record** (item 18). Half a day for the record; the code follows.
- **A rung-0 row in `Confinement.tla`** (accounting discrepancy 8). Half a day.
- **The ADR-0036 ratification run** (item 34). One to two days, and everything it needs is already in `slm/serve/`.
- **Driver scripts and the broken jar path** (CR-23). Hours. The run script for the rules floor hardcodes a path that no longer resolves.
- **Register lag** (CR-25, item 38). Hours. The gaps file's evidence row still describes the 38-test run; the derived set from 09.12 to 09.17 is stale and cheaper to retire than regenerate.
- **Persona expiry** (item 21) and the **verifier key amendment** (item 27). One to two days each, both single-record.
- **ADR-0021 reconciliation** (item 4). One to two days: one clause against ADR-0003, then a batch.

## 3. Least in scope, best delegated to the TCB

These should become declaration rows, each with its residual stated, rather than code or new mechanism design.

- **Replica authentication and Byzantine replicas** (G5, item 23). Replicas are already inside the trusted base by ADR-0033 §3. Mutual TLS is commodity platform work. Keep crash-recovery, state the forged-admit residual, and do not build BFT, which the estimate puts at weeks.
- **Native tool hermeticity** (G4). ADR-0034 discharges it for Wasm by construction and makes a native tool D-0034-3. Declare native tools out rather than building a behaviour checker.
- **Rung 2 and 3 substrate** (item 29, accelerator attestation). The hypervisor, firmware, CPU root of trust, verifier and confidential-compute accelerator are TCB rows by definition. TOPAK owns P7's reference values and a revocation-by-profile-digest rule for withdrawn firmware, nothing more.
- **Key custody and the anchor ceremony** (G6). Secrets in the clear belong in an HSM or KMS. ADR-0025 already makes custody a declaration; TOPAK owns the `Authentic` rule, not the vault.
- **Trusted time for R8** (G10, item 8). ADR-0032 says a TTL needs trusted time. A time source is exactly the kind of assumption that goes in the declaration, and until one is declared the epoch-lapse stand-in is the honest answer.
- **The solver** (item 15). ADR-0030 already names the engine-divergence residual as a TCB entry. Write the row; do not try to verify cvc5.
- **The archive store** (G9, item 28), partially. The store itself can be substrate with object lock. The forensic horizon and the audit read path grant authority and stay TOPAK's.
- **Log compaction and snapshots** (G14). Service engineering, fine for a baseline, no design content.

**Two that look delegable and are not.** The gate runner (G8) and the rung-1 launcher both fail the delegation test: a forged "gates passed" or a launcher that lies adds authority. The runner can be substrate, but its evidence must be signed by a key carried in issued rules, the same shape ADR-0034 §2 gives the verifier.

**Deferrable rather than delegable:** erasure (G11, nothing to exercise at genesis), per-principal ordering (G15, waits on ADR-0005), floor fitness (item 2, an open research question), and re-genesis migration (item 10).

This repository's Claude settings deny file writes and pushes, so this stays a chat answer. It fits the `derived/` convention as a dated analysis if you want it committed.
