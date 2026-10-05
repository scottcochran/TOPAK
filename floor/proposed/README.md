# Proposed policy floor

**2026.10.04**, revised 2026.10.05 · DRAFT · not ratified · **the reference links the `control` stage** (since 2026.10.05)

This directory holds the floor as it would read if the records drafted on 2026.10.03 and 2026.10.04 were in force.
**Since 2026.10.05 the reference links, pins and replays a stage from here** (`mechanism/crates/topak-floor`), switched
outright from the genesis floor in `floor/` at the custodian's direction: `labels` at commit `c15026d`, and `control`
after it. The `emergency` stage is loaded by nothing. The stage files open with a comment that says they are not
what the reference follows; for `labels` and `control` that is no longer true. The bytes are left as they were gated, so that the digests the gate results and
ADR-0047 cite are the digests the reference pins, and the comment is corrected at the stage's next gate run.
It exists so that those records' floor text is real Cedar that has been validated, tested and put through the
gates, and not a table in an amendment.

## Stages

Each stage is the previous one plus the entries one batch of records asks for, so a stage can be adopted without
the ones after it.

| Stage | Records | Change to the floor | Policies | Cases |
|---|---|---|---|---|
| `labels` | ADR-0047, with ADR-0048 and ADR-0049 (ADR-0041 A1; ADR-0030 A2) | Three forbids on `Actuate`: `R5`, `R6`, `R7` | 20 | 74 |
| `control` | + ADR-0050 (ADR-0041 A3) | Six actions and nine entries for an `operator` seat: `C1` to `C9` | 29 | 106 |
| `emergency` | + ADR-0052 (ADR-0041 A2) | `X1-break-glass` removed; `B10` admits the `emergency` kind for `Actuate` | 28 | 107 |

The genesis floor has 17 policies and 62 cases.

## Files

| File | What it is |
|---|---|
| `build.py` | Builds every stage from `../genesis.cedarschema`, `../genesis-floor.cedar` and `../genesis-tests.json`. Each edit to the genesis text replaces a string asserted to occur exactly once, so a change to the genesis floor that this file does not expect stops the build |
| `<stage>.cedarschema`, `<stage>-floor.cedar` | The stage's schema S and floor. Generated; edit `build.py` |
| `<stage>-tests.json` | The stage's behavioural cases. Generated. `control-tests.json` is tracked, because the reference's floor tests replay it; the other two are not (about 2 MB) |
| `run-gates.py` | Drives `../run-gates.py`, the genesis gate runner, unchanged, on a stage, then adds routing controls for the new entries |
| `<stage>-gates-results-2026.10.04.txt` | The gate run for each stage. All gates pass in all three |

## Running

```sh
export PATH="$HOME/.cargo/bin:$PATH"                      # cedar, built with --features analyze
export CVC5=/path/to/cvc5                                 # cvc5 1.4.0, as for the genesis gates
python3 build.py
for s in labels control emergency; do
  cedar validate  --schema $s.cedarschema --policies $s-floor.cedar
  cedar run-tests --schema $s.cedarschema --policies $s-floor.cedar --tests $s-tests.json
  python3 run-gates.py $s $s-gates-results-<date>.txt
done
```

A rerun of `run-gates.py` reproduces each results file byte for byte, evidence digest included. The evidence itself
(every solver query, its proof and the checker's verdict) is left in a temporary directory and not copied.

## The entries

**Labels** (ADR-0047 §7, F1 to F3). Each is a forbid on `Actuate`, a set-membership test on attributes the mechanism
computed. They deny whatever permit is satisfied.

| Id | Refuses an outward call when |
|---|---|
| `R5-no-read-then-send` | `clearSet` holds `untrusted`, and `restricted` is in `clearSet` or in `inputLabels` |
| `R6-no-steered-destination` | `clearSet` holds `untrusted`, and a destination input is a literal |
| `R7-no-replayed-destination` | a destination input is a handle whose label holds `untrusted` |

**Control** (ADR-0050 §4). Four permits and five forbids over six new actions.

| Id | Kind | Says |
|---|---|---|
| `C1-regrant-successor` | permit | An operator grants a seated target's next round, in its own domain, with the same binding and an alphabet that is the last one's or narrower |
| `C2-renew` | permit | An operator renews a live lease in its domain |
| `C3-attest-gates` | permit | A Build operator records that the gates ran |
| `C4-deny` | permit | An operator whose Persona is in force ends a round, revokes or fences, under a live lease or on a fresh sign-on assertion |
| `C5-add-needs-lease-and-peer` | forbid | No add without a live lease and a live peer |
| `C6-no-self` | forbid | No regrant or renewal of oneself |
| `C7-fence-needs-lease` | forbid | No fleet fence without a live lease |
| `C8-task-label-in-bounds` | forbid | No regrant whose task is unlabelled or labelled outside its seating's bounds |
| `C9-stop-in-own-domain` | forbid | No ending of a round or revocation outside the operator's domain |

**Emergency** (ADR-0052). No new entry. `X1-break-glass` is deleted and the `breakGlass` fields leave the schema. An
`emergency` seat's calls are admitted by `R1-actuate-allowlisted` over the envelope it was given. `R3-observer-live`
is unchanged and does not reach the seat, because R3 names `thinker` seats. `B10-only-thinkers-author` gains one
exception: an `emergency` seat, for `Actuate`.

## What the schema gains

| Stage | Addition | Who writes it |
|---|---|---|
| `labels` | `Tool.outward`; in `RunCtx`: `clearSet`, `inputLabels`, `destLiteral`, `destLabels` | The lift, from the record and the entry of the granted bundle revision. `outward` is derived from the issued rules' list of inside targets and is never declared |
| `control` | The kind `operator`; the entity `Fleet`; `ControlCtx`, thirteen facts about the operator, the target and the request; six actions | The mechanism. An operator supplies none of them |
| `emergency` | The kind `emergency`; `RunCtx` loses `breakGlass` | — |

## What the gates show, and what they do not

Each stage passes the genesis gates as they stand: totality for every policy on every action it applies to;
non-vacuity and discrimination on every action; every entry matters; the four genesis routing candidates; the
negative controls; the three checker controls. Added per stage: a candidate that drops or weakens a new entry is
classed a relaxation, and one that strengthens it a tightening (four candidates for `labels`, nine by `control`,
eleven by `emergency`). No `holds` in any run is without a checked proof.

- **This is the admit-time half.** ADR-0047's F4 to F6 are checks on bundle data at load (ADR-0049 §6, W7 to W9), made
  by the mechanism. They are not Cedar and are not here.
- **The floor trusts its inputs.** `clearSet`, `destLiteral`, `peerLive` and the rest are facts the lift supplies. That
  the lift computes them correctly is what `spec/Labels.tla` and `spec/Operators.tla` model, and what the reference
  would have to do. The reference's lift supplies none of them today.
- **`sameBinding` and `nextRound` are compared by the lift**, not in Cedar: the round comparison is arithmetic on a
  `Long`, which the totality gate refuses because it can overflow. The alphabet comparison is in Cedar.
- **`C9` is not in ADR-0050's first list of eight.** Writing the entries showed that "a lapsed operator stops its own
  domain" needs a rule about domains, and that it should bind an operator with a live lease as well. ADR-0041 A3
  carries it.
- **Break-glass in the first two stages is the genesis one.** `R5` to `R7` hold under `X1` there, and the tests say so.
