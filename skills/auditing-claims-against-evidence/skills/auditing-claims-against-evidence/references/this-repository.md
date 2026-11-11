# In the TOPAK repository

Everything else in this skill is general.

## Where the evidence is

| Claim about | Compare with |
|---|---|
| A record's status | Its `**Status:**` and `**Pending:**` lines. A batch mark on the status line is what says it was applied |
| A pending change | The History row's state, and whether the amendment says "Takes force only with" |
| A TLC result | `spec/<Module>-results-<date>.txt`; `<Module>_proof.tla` does not exist if no proof does |
| A TLAPS result | `spec/<Module>-proof-results-*.txt`, and `-proof-cert-results-*` for what certified. LS4 steps are not checked by anything |
| Currency of proofs | `spec/proof-sync.sh` |
| A Lean result | `spec/lean`, `mechanism/lean`, `floor/lean` results and READMEs; currency by `tools/lean-sync.sh` |
| The trusted base | ADR-0045 Annex A and B |
| A manifest | `tools/verify-manifest.sh <name> <commit>`; `--all` |
| A premise or route | `spec/theorem-premise-binding.md`, newest `spec/premise-routes-results-*` |
| Whether an action is permitted | The Cedar of the stage the claim is about, `floor/genesis-floor.cedar` or `floor/proposed/<stage>-floor.cedar`, and its schema. The floor is default deny. A floor entry in an ADR's table is a statement until it is written in Cedar, and the mechanism's own checks are in `mechanism/crates/topak-core` |
| What counts as an effect | ADR-0042 §2, and ADR-0015 for what is enumerated |

`tools/lean-sync.sh`, `spec/proof-sync.sh` and `spec/specification-graph.py check` do not all pass today, for known
reasons in the G11 open list. A failing exit status is not a finding by itself; what it names may be.

## Vocabulary

**Proved** is reserved for TLAPS (ADR-0046 §1). **Proved in Lean** names the kernel, of the encoding, transcription or
statement (ADR-0053 §1). **Checked** is TLC at small constants. **Certified** is the checked-backend run. A TLC-only
module is not proved. A Lean theorem about a model of `State::apply` is about the model.

Resolution order when documents disagree is in the reviewer's guide §3. The checkpoint wins over the narrative.

## What an audit does not satisfy

ADR-0029 A2.1 asks for a reviewer who is not the author, and history rows say **Not reviewed by a reader other than the
drafter** (ADR-0029 A2.5). An agent's audit does not change that sentence, unless the custodian rules that it does. A
ratification condition that says "a reader who is not the drafter" is not met by this. Say so whenever an audit is
offered as one.

Findings go to the custodian. Corrections are `drafting-records` acts: an R-revision on a Proposed record, a pending
erratum or amendment on an accepted one.

External sources are usually not in the tree. `derived/` documents repeat citations, and are not the source.
