I'll start by finding what "contain" and the "gap" refer to in this repository before answering.

I'll read the remaining sources: ADR-0022's confinement obligation, ADR-0031's lease confinement field, CR-1 from the critical review, the reference's front-door note, and the 09.17 narrative log on the "container vacuity" sessions.

The gap is fully specified on paper and enforced nowhere. Two Proposed records and one checked TLA+ module define what `Contained` means and how a principal gets in, but the reference still issues every lease at rung 0, so the set the safety theorems quantify over has no members. Your two options are not alternatives. Option 2 is the first step of any closure, and option 1 as stated points at the wrong object.

## What is already accounted for

- **The instant and the field.** ADR-0031 (Accepted, C1) puts confinement in the lease as a profile digest plus an attestation rung, makes the grant the moment `Contain` learns what it runs inside, and fixes rung 0 as `Mediated` always. `Rung0NeverContained` is checked in `spec/Lease.tla`.
- **The rungs, the profile, and the predicate.** ADR-0034 (Proposed 09.25) defines rungs 1 to 3, the seven-clause confinement profile, appraisal ordered at grant with three verdicts and no silent downgrade, and states `Contained(p)` in §4: a live lease at rung 1 or above on an Attested verdict, a profile meeting P3 to P5, and an in-house Persona on ADR-0017's axis. It explicitly makes lineage independence *not* a conjunct. Once it is in force, `Contained` is reachable at provenance rung 1.
- **The model-level witness.** `spec/Confinement.tla` was run 09.25. `Safe` holds at every rung, `NeverContainedEffect` is violated at rungs 1, 2 and 3, so a `Contained` principal acting is reachable in the model, and the `M_HOST` mutation breaks rungs 1 and 2 while changing nothing at rung 3. The rung ladder is checked, not asserted.
- **The provenance half.** ADR-0035 (Proposed) writes the independence criterion as an exclusion rule over log-projected lineage records. It only matters for the *archetype's* `Contained` set, and its projection needs ADR-0034 in force.

## What remains

- **Neither record is ratified**, and both carry confirmation markers (C2 and C4). Until then the text of record still says `Contained` is unreachable at every rung, and ADR-0034 finding 1 already flags that sentence as stale in the Theory of Operation, the glossary and G3 item 20.
- **No mechanism.** Gap G1 in `mechanism/GAPS-AND-ASSUMPTIONS.md`: every lease is rung 0, and the MCP front door is the whole protocol but not the whole channel. ADR-0034's own open obligation names the smallest step: a rung-1 launcher in the node, which needs a profile artifact, a guest image and the session binding.
- **The code encodes the pre-0034 definition.** `is_contained()` in `mechanism/crates/topak-core/src/lease.rs` requires the provenance criterion as a conjunct via a constant fixed to false. ADR-0034 §4 removed that conjunct. Ratifying 0034 makes this line wrong, not merely incomplete.
- **Run is blocked separately.** No record defines Run's alphabet (G3 item 13), so Run principals are `Mediated` at every rung whatever the confinement.
- **Native tools void it.** D-0034-3: any principal whose alphabet reaches a native tool is `Mediated`. The SLM trainer is native, so the rehearsal rounds stay declared even at rung 1.
- **Rung 3 debts.** The verifier key in issued rules (ADR-0025 §1 amendment), the TCB declaration record, evidence retention, accelerator attestation. All are archetype costs, not nonvacuity costs.

## The two options

**Option 1, define an occupant.** The corpus's own first principle is "verify the cage, not the occupant." The occupant is Byzantine by premise, so its identity never enters a theorem. What is actually undefined is the *cage instance*: a promoted profile, a measured guest image, a launcher, and a session bound to the launched guest. LangGraph specifically fails the profile on its face. A LangGraph agent calling a hosted model is prompt egress, which ADR-0031 §3 already rules `Mediated` regardless of rung, and P1 forbids the network device it would need. A LangGraph loop around a local in-house model could sit inside the guest, but then LangGraph is incidental plumbing that puts a Python runtime and its dependency tree into the promoted image, which at rung 3 is a trusted-base row. A minimal inference loop that speaks the six MCP tools over one channel is a smaller occupant. If the intent is instead to use LangGraph as a study object to derive Run's alphabet, that would give Run an alphabet shaped by a framework's affordances rather than by its effects, which is the opposite of how Build's six variants were derived.

**Option 2, shrink to nonvacuity.** This is the corpus's own discipline applied to its largest gap: the witness that must be violated, now at the running-code level rather than in TLC. Concretely:

1. Ratify or at least freeze ADR-0034, since nonvacuity needs a definition to be non-vacuous against.
2. Build the rung-1 launcher: the node launches a no-network, no-shell guest with workspace and corpus mounts and a single channel to the front door, and asserts the profile digest and instance in the grant. Bind the session to that instance in place of the bearer token.
3. Use the `slm/` model as the in-house Persona in the guest. It satisfies the third conjunct and does not need to be useful, only possessed.
4. Grant that principal an alphabet without `Invoke`. That sidesteps D-0034-3 without Wasm tools, and renewal already permits a narrow alphabet.
5. Rewrite `is_contained()` to ADR-0034 §4, drop the provenance constant, and add an end-to-end test: one admitted effect with `contained` true at rung 1, a rung-0 principal beside it for discrimination, and a documented `NeverContested` at rung 1.

What that buys is honest and small. `Contained` gains a member, declared as D-0034-2, resting on a named trusted-base entry (the launcher) rather than on nothing. It converts "the design is safe about a set that might be empty" into "safe about a set with one member under a declared degeneracy." It does not discharge A1 as a mechanism claim at archetype strength, does not touch Run, and does not answer CR-1's demand for a real sandbox at rung 3. ADR-0034's options table already says this about rung 1: the first step, not the target.

**Recommendation.** Do option 2 as written above, then rung 2 (a TPM quote appraised by the mechanism) as the next increment, and treat rung 3 as the archetype cost it is. Along the way, fix the stale "unreachable at every rung" sentences in one pass, and split G3's open item 1 into the design half, which is done, and the mechanism half, which is not. If you want a concrete occupant for the reference, it is the SLM in a measured image, not an orchestration framework.
