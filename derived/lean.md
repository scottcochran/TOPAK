Still surveying the repo: I've looked at the TLA+ specs, proofs and Cedar floor, and now I'm checking what the existing proof certification leaves trusted.

**Short answer:** start with the admit-path composition (`FloorComposition` together with `admit.rs`), then the small set-theoretic modules, then the Cedar floor. The Cedar floor matters because Cedar's own semantics and its symbolic compiler are already formalized in Lean. Paxos is a good target but a big one. The operational model, transport and containment layers are the least suited.

Nothing in the repo uses Lean today. All the deductive work is TLAPS, plus the certification run described in `spec/proof-certification.md`.

## Ranked by how easy they are to formalize and how much you gain

**1. The admit composition: easiest, and the biggest gain.**
- `spec/FloorComposition.tla` (158 lines) is proved in TLAPS with no assumptions. Its five theorems include `AdmitImpliesFloorPermit` and `BundleCannotWriteFloorInputs`.
- The Rust it describes, `compose` and `floor_gate` at `mechanism/crates/topak-core/src/admit.rs:64-87`, is about 20 lines of pure pattern matching over enums.
- In Lean you could prove the theorems directly about a translation of that Rust code. Tools that translate Rust to Lean (Aeneas or hax) would produce it, but I haven't checked that either handles this crate.
- That would attack T-0045-28, "the running code refines the checked spec." TLAPS cannot reach that row, and today only trace replay through `Mechanism.tla` covers it.

**2. Small finite-set invariants with no assumptions.**
- The modules are `Seats`, `Observers`, `RunSeats`, `FloorRouting`, `NonComposition`, `Anchor` and `BreakGlass`.
- Each is an invariant over finite sets and records, and the existing proofs mostly need no hypotheses.
- In Lean these become induction on reachable states, closed with `simp`, `decide` or `Finset` lemmas.
- That removes the 74 LS4 temporal steps that §5a of `spec/proof-method.md` lists as checked by nothing. "Holds initially, every step keeps it, so it holds always" is just an induction in Lean, checked by the kernel.

**3. The Cedar floor (`floor/`).** AWS keeps Cedar's semantics, validator and symbolic compiler (SymCC) formalized in Lean, in the `cedar-spec` repository. That means:
- You could restate the ADR-0030 §5 gates (totality, non-vacuity and the rest) as theorems about `genesis-floor.cedar` under Cedar's Lean semantics.
- You could close the `holds°` results. Those are verdicts cedar reaches by its own term folding, with no solver query, and they rest on T-0045-3 today.
- The thing to confirm first is that the Lean model's version matches the `cedar-policy` 4.13 the mechanism links.

**4. Parameterized arithmetic: where Lean beats the SMT route.**
- **`Coupling` / `UnreadBounded`:** it is stated "for every K, R, MaxRound". Lean's `omega` tactic handles this kind of linear arithmetic over naturals.
- **`Lease_A1` and `subtracting_interval_elapsed`:** this is the clock check at `topak-core/src/clock.rs:41`. Small enough to prove at the code level too.
- **`RulesFloorNV_rev5`:** it uses quorum thresholds and counted seats (`Cardinality`), which map onto Mathlib's `Finset.card`. It is one of the three modules that do not certify, because Isabelle refused one of Zenon's proofs.
- **`Confinement` and `Confinement_A1`:** they don't certify because three `TypeOK` steps in each are proved only by Z3. Lean could supply fully checked proofs of the same claims without editing those frozen modules.

**5. Paxos: valuable, but harder.**
- `topak-paxos` is sans-IO: each replica is a pure function `handle(Input) -> Vec<Output>`, which suits a refinement proof.
- `voting.rs` is the abstract voting layer that the simulation checks. Its `OneValuePerBallot` and agreement are the classic Paxos safety proofs, and there is precedent for doing them in Lean.
- The TLA+ `Paxos` module the Theory of Operation calls for is unwritten (finding 9 in `mechanism/GAPS-AND-ASSUMPTIONS.md`). Lean could fill that gap rather than duplicate existing work, but expect weeks of effort, not days.

**6. The theorem-premise matrix.** The inventory formula, holds = ¬(B·¬d), is plain Boolean algebra, so its properties are easy to prove. One example: declaring more trusted-base rows never makes a theorem void. It's cheap but low value, since `inventory.py --check` already covers most of it.

## Least suited

- **`Mechanism.tla`** (720 lines): it is deliberately "pinned, not frozen" and changes with the code, so a proof would keep breaking.
- **`Labels`:** a 742-line proof that is still Proposed. Wait for it to settle.
- **The Rego bundle:** Rego has no Lean semantics. You also don't need one, because the composition theorems already make bundle behaviour irrelevant to floor safety.
- **Kafka transport, MCP, the container launcher, attestation (T-0045-16) and the SLM:** these are empirical or depend on external systems.

## Before starting

- **A Lean proof of a TLA+ module covers a Lean re-encoding of it, not the frozen text.** That translation becomes a new trusted-base row, unless you embed TLA+ semantics in Lean, which is a project of its own.
- **Lean would be a new prover in the trusted base.** ADR-0046 made TLAPS a row (T-0045-31), so the corpus's process would want a record before any Lean result is cited. Lean's small, independently re-checkable kernel makes that an easy argument.

My recommendation: do item 1 first. It is small and pure, and it is the one result TLAPS cannot produce: a proof about the Rust code that runs.
