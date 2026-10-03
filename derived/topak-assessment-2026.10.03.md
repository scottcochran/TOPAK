I'll survey the TOPAK repo first to understand what it is and where it stands, then assess it on those three axes.

This is a design corpus with a state-of-record checkpoint (G9) and a fresh critical review. I'll read those, the proof results, and the mechanism gaps doc in parallel.

The critical review and gaps doc were saved to files. I'll read the critical review fully, the findings section of the mechanism gaps doc, and the proof-sync state.

I'll read the 10.02 critical review in full since it's the freshest source, along with the current gap register and a live health check of the tree.

I've got most of the picture now. Next I'll check the review's findings section (CR-27 to CR-39) and verify the tags and manifest against the remote, since this is a shallow clone and the local tag list was empty.

Tags do exist on origin, confirming G9 item 79 is stale per the review's CR-31. Now that cloning is done, I'll run the manifest verifier and spot-check a few review findings at HEAD.

The G9 checkpoint is the state of record, and the 2026.10.02 critical review is one day old, so the assessment below is anchored on those two, cross-checked against the tree. What I verified live here: every one of the 21 manifests verifies at its commit, the G9 manifest at HEAD fails only the two narrative files revised after the cut, all 15 proofs are in sync with their modules, and the reference checker's seven missing paths are all known installs or the `tools/call` false positive. I did not re-run the TLAPS proofs, the Cedar gates, or the Rust tests. The prover, cedar, cvc5 and ethos are not installed in this container.

## 1. Easy wins

Each is under a day and waits on no decision.

- **Repoint the register.** `README.md:20` still names revision 12 and G8. G9's header says revision 12 stands "not revised at G9", and item 79 says the tags `ToO-rev12`, `glossary-2026.10.02`, `REF-2026.10.02` and `REF-2026.10.02b` do not exist. They all exist on origin, as does `ToO-rev13`, and revision 13 is committed. This is CR-31, and it is the class of error a second reader catches first.
- **Add the ADR-0029 A2.5 ledger line.** A2.5 requires the debt ledger to say whether a bootstrap reviewer is engaged and the digest of the last review pass. G8 §4 and G9 §4 carry no such line. Writing "none, none" is honest and makes the blocking gap below visible on the ledger.
- **De-flake the launcher tests.** `mechanism/crates/topak-node/tests/contain.rs:315` sequences launch, fence and assertion with a `settle` helper and a 500 ms sleep at line 647. Wait on the returned log index instead. These tests are the evidence the pending A7 addendum cites, so a test that can fail for want of time can also pass for want of time. ADR-0032's own clock rule says why.
- **Fix two live miscitations in revision 13.** `narrative/theory-of-operation.md:945` attributes the human-reviewer half of "unanimous humans fail together" to Moon & Varshney §4.6, which says nothing about humans. Line 1068 still says promotion "enters `Build(Contain)` enforcement coverage", which has been CR-8 since 09.16.
- **Write the residual-risk statement.** Named the highest-leverage single document in four reviews running. Its text already exists in ToO §12 and §13, ADR-0045 Annex A's residual column and the gap premises `spec/inventory.py` prints. It discharges MANAGE 1.4, MEASURE 2.6, GOVERN 4.2 and the `T_irrev` declaration at once.
- **Pin the prover.** The `tools/tlapm` wrapper execs an untracked 1.9 GB build known only by the digest each results file prints. Adding its digest to a manifest closes item 73 in an hour and halves CR-30.
- **Record the six conversation-accepted choices.** G9 §1.2 lists six reference behaviours accepted in chat and carried as PROVISIONAL tags. Each is a short record entry: the per-seat rung to ADR-0023 §6b's template, withdrawal and the Contested rule to ADR-0034.
- **Regenerate the Playbook artifacts.** The 09.12 inventory and 09.15 feature list have been "due" since revision 7. Table 1 of the 10.02 review is the finished input.
- **Build the P3-passing image.** A static build on an empty image has been "the step" since ADR-0036 was drafted on 09.27. It is one to two days, so at the edge of easy, and it is the cheapest change with the largest effect on every grade: the first candidate member of `Contained` under a declared profile.

## 2. Most blocking gaps

In order of what each blocks.

1. **No second reader.** Forty records accepted, 22 confirmation-required, seven assistant-drafted texts with four in force, and the pending A2, A7 and A8 have their code, modules, proofs, mutation tests and traces from the same hand in one day. ADR-0046's ratification condition was met in letter, not purpose. This blocks bootstrap eligibility, every confirmation, and safe ratification of the pending cluster. Nothing in the repository can close it.
2. **The sandbox gap.** No real principal is `Contained`. Rung 1 trusts the host by construction and both rung-1 profiles declare a failing P-conjunct. Rung 3 is two test keys. Rung 2 is a seam. Even a real rung 3 would not be `Contained`, because `Rules.criterion` is unset in every shipped rules file, so ADR-0035 has to reach issued rules. Until this moves, effect exclusivity is an assumption identical in strength to the paper TOPAK measures itself against.
3. **The pending ratification cluster.** ADR-0034 A2 with ADR-0042 §6, then A8; ADR-0036, then A7. Until these land, Run principals are `Mediated` by the records whatever the lookup computes, and the launcher is cited by nothing in force. CR-33 is the warning: A2's three drafter's choices are exactly the ones the reference then narrowed. The Wasm component became a core module, the protocol is recorded not enforced, and a Run tool's channel is declared twice and never reconciled. Build's P4 is not enforced at all. So this gap loops back to gap 1.
4. **Break-glass is both too hard and too easy.** R3 couples every effect-bearing Run admit to a live Observer, break-glass included, so the emergency path waits on a dead Observer. R8 is still pending with four unmet conditions, so an approval is time-unbounded within an epoch. Both fixes are small and both are decision-blocked.
5. **The untyped operator channel.** Grants, launches, revocations, issuances, `GatesPassed` and profile registration are authenticated by a socket file mode. Replica traffic is unauthenticated, the only trust-root row whose named mitigation is unbuilt. Gate evidence is an operator's assertion. This is the half of the control-plane alphabet that can add authority, and it has the least type discipline.
6. **The refinement.** Every property for a running deployment is conditional on T-0045-28. The trace harness is stage one and covers tested paths only. Stages 2 and 3 and the reproducible build are the long-term block.
7. **Three threats with no record and no owner.** Delegation and chains, the fourth review to say so. Flow constraints. Prompt injection inside the envelope and unpinned tool descriptions. The provenance-label record is the highest-leverage single ADR available.
8. **Every number is a placeholder.** No Observer has been measured, and the `slm/` rig could measure `T_obs` and `K` today.

## 3. Proof-exposed issues

Two readings, both relevant.

**What writing the proofs found.** `spec/proof-method.md` §1 and G9 §3 record these.

- **Five premise-table corrections.** RunSeats' `M_OBSEMIT` breaks none of its three invariants. Confinement's `SameGuest` check at grant is not load-bearing; `Act`'s generation check is. In FloorComposition, `M_OVERRIDE` and `M_ERR` each break more properties than the table listed, in rows the original results file never ran. RunCoupling's `SealCountsEffects` breaks under `M_EMITSEQ`, not `M_ROUNDS`. The `K < R` premise was struck from the unread bounds, which are proved for every K and R.
- **A missing clause in NonComposition.** The proof needed "only admitted effects are recorded as via break-glass", a fact no TLC run could reach.
- **A case split the drafter said would not change.** Finding 6's successor proof had to split on `Declared = 1` at the one step that expands `Evidence`.
- **Unnamed module ASSUMEs are not used by the prover.** The genesis facts in Anchor and BreakGlass are now lemmas, and RulesFloorNV_rev5's three ASSUMEs are proved with witness records.
- **The floor base was mis-described as frozen.** ADR-0046 E1 corrects it: `RulesFloorBase.tla` is live, and R8's ratification will make `Anchor_proof` and `BreakGlass_proof` stale and require successor proofs. That cost is known in advance.

**What is exposed about the proofs themselves.**

- **Same hand, one day.** Fifteen modules, 3,036 obligations, every hypothesis derived from the mutations by the author of both. The honest reporting in G9 §4 and §8 is a report, not a review.
- **The checker asymmetry.** The corpus refused cvc5's `unsat` as evidence and put a pinned proof checker behind the floor gates. The same day's obligations are accepted on tlapm's word, discharged by Z3 4.8.9 and Zenon with no certificate. The Isabelle backend that would check them is unused, and the prover is untracked. Running Isabelle once over the fifteen modules closes it.
- **No liveness anywhere.** Every module is `Init /\ [][Next]_vars` without fairness. `grep` confirms no `WF_` or `SF_` in `spec/Coupling.tla` or `spec/RunCoupling.tla`. The method note says this is why the proofs were cheap. For a design whose Run posture is "stall", the model cannot distinguish stall from deadlock. One liveness property under weak fairness on the heartbeat would be the first proof here that could be false.
- **The hard half was excluded by construction.** The prover proves universal statements. Every existential claim, that a mutation reaches a bad state or a witness is reachable, stays with TLC at small constants, and item 75 says practical constants are unrun.
- **Proved of the modules, not of the reference.** At the reference, `ContainedMeansConfined` and `ContestedStopped` are void. `NoSilentDowngrade` and `FreshAppraisal` hold on traced states only. `Mechanism.tla` is a trace replay and is unproved by design.
- **Proved over placeholders.** The proofs show `K < R` is needed for the coupling bound to refuse at all, and cannot say what `K` should be.

The one item that moves all three lists is the same as in the 09.25 and 10.02 reviews: engage one reviewer who is not the author, and write that fact on the A2.5 line.
