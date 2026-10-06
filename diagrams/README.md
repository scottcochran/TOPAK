# Diagrams

Diagrams of the corpus and the generators that draw them. A diagram is a derived artifact: it describes the
records and never decides anything. **Where a diagram and a record disagree, the record wins**, and the state of
record is the latest checkpoint.

## The TOPAK diagram family (2026.10.05)

Thirty-nine diagrams covering the pattern's logical hierarchies and domain boundaries, drawn against Genesis
Checkpoint G10 (2026.10.05) and Theory of Operation revision 14. Each diagram is an SVG that adapts to light and
dark themes (`prefers-color-scheme`; renderers without CSS fall back to light). The diagrams are sized for
reading zoomed in and print at poster scale. Where a record has a table, the diagram draws all of it.

**Revised 2026.10.05** against G10 and ToO rev 14. Every diagram of the 2026.10.03 family is redrawn to Batches 27
to 35, and seven are new: the floor in force and its three gated stages (B8), labels and handles (C6), the tool
list and the allowlist entry (C7), the operator as a principal (C8), break-glass as an emergency seating (D5), the
correlator's folds (E3) and proof certification (H6). Two statuses are new to the family's language:
**provisional** (ADR-0029 A4; ADR-0050, ADR-0052 and the amendments that rest on them), drawn as a dashed blue
pill, and **genesis-provisional** (ADR-0030 A3; the policy floor), drawn as a dashed violet one. X1 is drawn
retired wherever it appeared, R8 withdrawn, and the unsigned operator socket is marked BOOTSTRAP. G3 opens with
the binding table's gap (G10 item 90): seven of the twenty-two proof modules have no row.

**Amended 2026.10.06** for ADR-0053 (**Proposed**, drafted after G10): the Lean route. One diagram is new, H7, and
ten are amended, each where the Lean results bear on what it draws: B3 (the genesis floor's totality under Cedar's
model), D2 (the composition proved of `admit.rs`), E2 (the clock check and `Coupling`), G1 (the proposed row
T-0045-37, drawn apart from the thirty-six), G3 (what the binding table would gain, and why no premise moves), H1
(the three `lean/` directories and the Lean tooling), H2 (ADR-0053), H3 (a Lean lane and a note per module), H5
(the Lean loop beside the TLAPS loop) and H6 (the Lean route beside certification). A fourth word joins the three:
**proved in Lean**, of an encoding, a transcription or a statement, never "proved" alone (ADR-0053 §1), and every
Lean statement carries ADR-0053's Proposed status. The files keep the family's date; the other 28 regenerate
byte for byte. Amended again the same day for ADR-0053 R4: H7 and H3 draw the model of `State::apply` that refines
`Seats`, and the replay of the reference's recorded traces through it; and for R5, the second model on it, with
`Coupling`'s properties, and its replay.

| Id | Diagram | What it shows |
|---|---|---|
| **A · Orientation** | | |
| A1 | [Roles map](topak/A1-roles-map-2026.10.05.svg) | T, O, P, A, K as roles with obligations; the reference's instruments at G10 and what it does not claim |
| A2 | [Two domains, one membrane](topak/A2-two-domains-one-membrane-2026.10.05.svg) | `Build(Contain) → Run(Contain)`: the gate, both alphabets and each domain's ingress (Run's four labelled items, handles, the tool list), the people-only `operator` and `emergency` seats (provisional), and promotion, which now seats, as the only crossing |
| A3 | [Boundary register map](topak/A3-boundary-register-map-2026.10.05.svg) | B1–B14 placed on one system picture; the full register, and what has changed since it was written, restated at G10 |
| A4 | [Orientation and monotonicity](topak/A4-orientation-monotonicity-2026.10.05.svg) | The orientation rule across the sixteen layers of ToO rev 14 §7.8, Ingress and Operation added, with where it is not yet whole |
| **B · Authority** | | |
| B1 | [Authority chain](topak/B1-authority-chain-2026.10.05.svg) | From the intent axiom to an effect, including who puts a lease on the log (a quorum's first lease, operators' signed requests under `C1`–`C9`, BOOTSTRAP), break-glass as an emergency seating, and the audit chain back up |
| B2 | [Verified object and edge](topak/B2-verified-object-and-edge-2026.10.05.svg) | What is proved once, against what may only subtract (B4); the 28 policies of the floor in force (genesis-provisional), one floor exception, X1 retired |
| B3 | [Floor change routing](topak/B3-floor-change-routing-2026.10.05.svg) | The computed route for a floor change, the proof-carrying gate, the three gates, the three-stage build of the floor in force, and every line of its gate run; the genesis floor's totality also proved in Lean under Cedar's model (ADR-0053, Proposed) |
| B4 | [Rules floor](topak/B4-rules-floor-2026.10.05.svg) | R1–R9 at G10 (R6 and R7 restated, R8 withdrawn), the issued things (a)–(h), parametricity, the non-vacuity runs, the proofs, and the `_A1` successors |
| B5 | [Promotion quorum](topak/B5-promotion-quorum-2026.10.05.svg) | Promotion as a round: gates, seats, recusal, tally, stalls; and since ADR-0024 A3 (provisional) a promotion seats: the first lease on the tally, an operator's successor grants, the first operators at bootstrap; BOOTSTRAP at the reference |
| B6 | [Anchor custody](topak/B6-anchor-custody-2026.10.05.svg) | The havoc issuer and what it issues at G10 (a provider's key, the two lists); the issuer now seats; the custody axis; who is at the gate |
| B7 | [Genesis to bootstrap](topak/B7-genesis-to-bootstrap-2026.10.05.svg) | Ratification to G10, the 28 confirmation-required records (two provisional), the A2.5 line, the trigger and the ceremony with the first operators and floor fitness |
| B8 | [The policy floor in force](topak/B8-floor-stages-2026.10.05.svg) | How `build.py` makes the floor in force from the genesis draft: the `labels`, `control` and `emergency` stages with each one's entries, schema changes, cases, digests and citing records; every gate per stage; the genesis-provisional status, the wrong opening comment, and all 28 policies |
| **C · Principals and the membrane** | | |
| C1 | [Principal, seat, cell](topak/C1-principal-seat-cell-2026.10.05.svg) | Deployment → domain → cell → seat and stage → principal → lease; the five seat kinds, including the people-only `operator` and `emergency` kinds (provisional); seatings; the per-seat declared rung |
| C2 | [Alphabets by seat](topak/C2-alphabets-by-seat-2026.10.05.svg) | Build's six variants, Run's three and the operator's control alphabet of six against five seat kinds; the floor in force in full; channel fidelity in force |
| C3 | [Lease anatomy](topak/C3-lease-anatomy-2026.10.05.svg) | The twelve fields and what travels beside them (no tool set); who grants and who denies (provisional); the life cycle, the fixed expiry race, and the one-round emergency lease |
| C4 | [Confinement rungs](topak/C4-confinement-rungs-2026.10.05.svg) | Rungs 0–3, P1–P7, verdicts, the four conjuncts of `Contained`; the Run profile in force (P4 as channel fidelity); the proofs, two not certified |
| C5 | [Rung-1 launcher channel](topak/C5-rung1-launcher-channel-2026.10.05.svg) | Launch, appraise, grant, bridge (ADR-0036, Proposed; the launcher built under ADR-0033 A7, ratified ahead of it); a `Regrant` at rung 1 must launch a guest, not built |
| C6 | [Labels and handles](topak/C6-labels-and-handles-2026.10.05.svg) | Run's four labelled items, delivery clear or by handle per seat kind, `clearSet` and the floor's `R5`–`R7` minimum, the R10 join `Labels.tla` found, the stale-`clearSet` refusal, the envelope's label fields, and what the label machinery trusts |
| C7 | [Tool list and allowlist entry](topak/C7-tool-list-and-entry-2026.10.05.svg) | ADR-0049's entry, its load checks W1–W10 and the two issued lists; the tool host reading the target from the entry; the tool list rendered and opening the round; no per-tool lease narrowing; what the reference does not follow |
| C8 | [The operator is a principal](topak/C8-operator-principal-2026.10.05.svg) | ADR-0050 (provisional): the operator seat and its six signed control actions mapped to `C1`–`C9` over thirteen facts; identity provider and key custody; the quorum path (not built) beside the BOOTSTRAP socket; `Operators.tla`; the exit from provisional |
| **D · Admit path and the record** | | |
| D1 | [Admit pipeline](topak/D1-admit-pipeline-2026.10.05.svg) | Decide, then order, then effect, with a denial lane; an operator's signed request and an emergency activation; the fourteen log-entry kinds; what `Mechanism.tla` checks against it |
| D2 | [Policy composition](topak/D2-policy-composition-2026.10.05.svg) | `admit ⟺ floor_permit ∧ ¬bundle_deny`, tier by tier, with the floor in force, the bundle's load checks, the label minimum no bundle can loosen, control requests decided by the floor alone, and schema S as of the `emergency` stage; the composition's truth table proved of `admit.rs`'s transcription in Lean (ADR-0053, Proposed) |
| D3 | [Record planes](topak/D3-record-planes-2026.10.05.svg) | Log, transport, archive and payload store; the round topic from its opening record to erasure; the `Actuate` record's label fields and `seatKind`; ADR-0005's roles; who reads a topic |
| D4 | [Privileged paths and forensic floor](topak/D4-privileged-paths-forensic-floor-2026.10.05.svg) | Erasure as the floor's one exception; X1 retired against what replaced it; NC-1, NC-2 in `NonComposition_A1`; F1–F6 with F5 as the activation record |
| D5 | [Break-glass is an emergency seating](topak/D5-emergency-seating-2026.10.05.svg) | ADR-0052 (provisional): the `emergency` seat, a seating activated for one person and one round by the roster's quorum, the domain's envelope and its open questions, no TTL, no Observer coupling, `Emergency.tla` and the `_A1` successors, the reference, and the exit from provisional |
| **E · Detection** | | |
| E1 | [Observer topology](topak/E1-observer-topology-2026.10.05.svg) | Cell Observers, the correlator, `W(p)` as the ACL, placement; what a cell Observer is given; operators and emergency seats as readers |
| E2 | [Liveness coupling](topak/E2-liveness-coupling-2026.10.05.svg) | `live(o)`, the `K` window, the clock model and the timing budget; an emergency seat uncoupled; the clock findings at G10; the clock check's arithmetic and `Coupling` proved in Lean (ADR-0053, Proposed) |
| E3 | [Correlator folds](topak/E3-correlator-folds-2026.10.05.svg) | ADR-0051 (Proposed, not built): what the correlator folds over, its tiers and correlations, findings, misses and the mark, its relation to `W(p)` and `K`, `Correlator.tla`, and collusion still failing open |
| **F · Model** | | |
| F1 | [Persona, lift and lineage](topak/F1-persona-lift-lineage-2026.10.05.svg) | The Persona, a person's Persona (provisional) and what the reference has instead, the split lift, and the lineage projection with ADR-0035 R5–R7 (Proposed) |
| **G · Trust and variation** | | |
| G1 | [Trusted base](topak/G1-trusted-base-2026.10.05.svg) | The admission rule and all thirty-six rows, with the reference's declaration and its rewritten paragraphs; T-0045-37, the Lean kernel, proposed by ADR-0053 and drawn apart (read from ADR-0053 at build time) |
| G2 | [Deployment lattice](topak/G2-deployment-lattice-2026.10.05.svg) | The archetype as unique maximum; every axis and declared degeneracy, with labels, the tool list, operators and the emergency path |
| G3 | [Theorem–premise DAG](topak/G3-theorem-premise-dag-2026.10.05.svg) | The binding table's gap at G10 (seven proof modules with no row), all 43 rows as chains, an incidence matrix and the full table, with proof and certification columns and the verdicts the records have overtaken; what ADR-0053 (Proposed) would add, 27 rows with a Lean route, and why no premise moves |
| **H · Corpus and implementation** | | |
| H1 | [Corpus structure](topak/H1-corpus-structure-2026.10.05.svg) | Layers, precedence, the checkpoint chain to G10 beside the narrative revisions, how a change moves, and what measures each part; the three `lean/` directories and the Lean pin and tools (ADR-0053, Proposed) |
| H2 | [ADR map](topak/H2-adr-map-2026.10.05.svg) | Every record, ADR-0001 to ADR-0053 (Proposed, after G10), by area, with status at G10 (provisional included), markers, amendments and dependencies |
| H3 | [Verification map](topak/H3-verification-map-2026.10.05.svg) | Every check and proof at G10: TLC on 27 modules, 22 proofs (5,225 obligations, 19 certified), floor gates on the genesis floor and the three stages, 133 tests, trace validation (82 traces), what must fail, and what none of it claims; the Lean route as a proposed sixth chain, and a Lean note on each module it covers |
| H4 | [Reference deployment](topak/H4-reference-deployment-2026.10.05.svg) | The reference as deployed in development and rebuilt in five stages on 2026.10.05: processes, the signed operator path and the BOOTSTRAP socket, the emergency activation, configuration, wire formats, and what is not built |
| H5 | [Proof anatomy](topak/H5-proof-anatomy-2026.10.05.svg) | How a proof is built and kept in step: one proof module part by part, the shapes its invariants took, what the newest proofs added, and the sync loop with the certified run beside it (ADR-0046; `spec/proof-method.md`); the same loop for a Lean re-encoding, row by row against the TLAPS loop |
| H6 | [Proof certification](topak/H6-proof-certification-2026.10.05.svg) | How every obligation of a proof module is accounted for by the route that closed it (ADR-0046 E2, A1), all twenty-two modules, the three that do not certify, and what a certified proof still trusts; which modules are also proved in Lean, and LS4 against the Lean route |
| H7 | [The Lean route](topak/H7-lean-route-2026.10.05.svg) | ADR-0053 (Proposed): three uses and one kernel, re-encodings, transcriptions and the floor in Cedar's model; how a Lean result is made, replayed and kept in step; the control that shows why `#print axioms` is not enough; two routes to the same theorems, module by module; what each route trusts; the proposed row T-0045-37; dependent entries, findings and open obligations. Reads the three Lean results files, `tools/LEAN-PIN`, ADR-0053 and the certified TLAPS results at build time |

### Regenerating

```sh
python3 diagrams/gen-topak-family.py          # all diagrams
python3 diagrams/gen-topak-family.py B5 G3    # some
```

The generator uses only the Python standard library. Each diagram is one module in `topak/src/`. Text is
measured with tracked font metrics and wrapped, so layouts are computed rather than hand-placed. The run prints
a warning for any overlapping text or partially overlapping block; a diagram is finished when it prints none.
G3 reads `spec/theorem-premise-binding.md` at build time, and the build fails if the table no longer matches
what the module expects; G1 reads `decisions/ADR-0045.md` the same way. H7 reads the three Lean results files,
`tools/LEAN-PIN` and `decisions/ADR-0053.md`, and H3, H6 and G3 read H7's list of re-encoded modules, so a Lean change
reaches every diagram that draws it. See [`topak/src/AUTHORING.md`](topak/src/AUTHORING.md) for the content rules and the
visual language.

## Earlier diagrams

| Diagram | Generator |
|---|---|
| [G1 → source control → bootstrap (2026.09.18)](g1-to-bootstrap-2026.09.18.svg) | [`gen-g1-to-bootstrap.py`](gen-g1-to-bootstrap.py) |
