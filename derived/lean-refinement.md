Let me read ADR-0053 and the relevant refinement-chain material.

**Officially, no; in substance, yes, in five places.** ADR-0053 states it plainly: T-0045-28 doesn't change and none of the refinement chain's three items is discharged (§6, Consequences). That reading is right. What changed is which next steps are cheap and what the chain will rest on.

**1. The chain's own plan already pointed at Lean.** ADR-0045 R2 and ADR-0033's open obligations define stages 2 and 3 as "a Lean model with differential testing, then its compilation." Until now nothing in the corpus used Lean. Now the tooling exists: a pinned toolchain (`tools/LEAN-PIN`), the `leanchecker --fresh` replay, `lean-sync.sh` for pinned-not-frozen files, and a proposed trust row (T-0045-37). So stage 2 no longer has to set up a new prover first; that part of its cost is paid. But what was built is not stage 2:
- Stage 2 is a Lean model of `State::apply`, the counterpart of `Mechanism.tla`, with the Rust differentially tested against it.
- What exists are hand transcriptions of two small leaf functions (`compose` and `subtracting_interval_elapsed`), read against the Rust rather than tested against it.

**2. The targets now exist in the same prover.** `spec/proof-method.md` says the real refinement target is from `Mechanism.tla` to the small modules. Twelve of those modules are now Lean transition systems, with `invariant` induction in `Prelude.lean` and invariants proved for every constant. So a refinement could be done entirely in Lean:
- Write the `apply` step as a Lean function.
- Give an abstraction map from its state to each module's state.
- Prove that every step maps to a module step or a stutter.

Each module's invariants then carry over to the model, with no TLC bounds involved. Findings 3 and 4 help here: `Confinement` holds for every `Declared`, and `Coupling` for every K and R, so the refinement doesn't need to match model-checking constants. The existing trace recorder (`trace.rs`) could also feed an executable Lean model instead of TLC. That is the "differential testing" half of stage 2, using traces you already produce.

**3. One refinement-shaped result exists, but it doesn't connect to a module.** `admit_iff` (`mechanism/lean/Topak/Admit.lean:302`) proves that the code's `compose` equals `tlaAdmit (floorPermit f) (bundleDeny b)`. That is an abstraction lemma, the shape a refinement step takes. But `tlaAdmit` is defined inside `Admit.lean`, and `FloorComposition` is not among the `spec/lean/` re-encodings. So the link to the module still rests on reading. The cheapest real increment is to re-encode `FloorComposition` in `spec/lean/` and prove the transcription refines it. That would be a small, kernel-checked refinement between spec and code, in one prover.

**4. Finding 2 becomes load-bearing.** A refinement done in Lean against Lean re-encodings would rest on T-0045-37 plus the fidelity of each encoding, not on T-0045-31. Its conclusion reaches the TLAPS-proved theorems only through the encoding premise. The premise table can't express "either proof" today. Once T-0045-28 is discharged through Lean, that open obligation has to be settled, or the table will misstate what the refinement's result depends on.

**5. On the admit path, ADR-0030's sense of refinement is now proved of the code.** In ADR-0030, refinement means the bundle refines the floor by composition. That is now proved of the code's composition, with the floor statement under cedar-spec's model. The one unproved piece left is `topak-floor`'s wrapper, which turns "Allow with no errors" into `Permit`. `mechanism/lean/README.md` says this under "Not the engines." Prove that, and the admit path's chain is complete except for T-0045-3 and the transcription premise.

**Caveats that still hold:**
- Transcriptions written by hand, by the same author, in the same days, run into ADR-0033's own point that one hand isn't independence. Aeneas or hax, the open obligation, is what would move that.
- Stage 3, "its compilation", would trust Lean's compiler. The floor package's `native_decide` already brings that trust in, in a small way, and T-0045-37 would need to cover it on purpose.

**Suggested order:**
1. Re-encode `FloorComposition` and prove the transcription refines it (small).
2. Prove the `topak-floor` wrapper.
3. Write a Lean `apply` model with an abstraction map to one module (Seats is the simplest), and replay the existing traces through it. That would be the first piece of real stage-2 work.

Then decide finding 2 before any addendum claims a stage is discharged.

I haven't changed or committed anything. If you want this as text for ADR-0033's open obligations or a finding in ADR-0053, I can draft it.
