# Diagrams

Diagrams of the corpus and the generators that draw them. A diagram is a derived artifact: it describes the
records and never decides anything. **Where a diagram and a record disagree, the record wins**, and the state of
record is the latest checkpoint.

## The TOPAK diagram family (2026.10.02)

Thirty-one diagrams covering the pattern's logical hierarchies and domain boundaries, drawn against Genesis
Checkpoint G9 (2026.10.02) and Theory of Operation revision 13. Each diagram is an SVG that adapts to light and
dark themes (`prefers-color-scheme`; renderers without CSS fall back to light). The diagrams are sized for
reading zoomed in and print at poster scale. Where a record has a table, the diagram draws all of it.

| Id | Diagram | What it shows |
|---|---|---|
| **A · Orientation** | | |
| A1 | [Roles map](topak/A1-roles-map-2026.10.02.svg?raw=true) | T, O, P, A, K as roles with obligations; the reference's instruments and what it does not claim |
| A2 | [Two domains, one membrane](topak/A2-two-domains-one-membrane-2026.10.02.svg?raw=true) | `Build(Contain) → Run(Contain)`: the gate, both alphabets, promotion as the only crossing |
| A3 | [Boundary register map](topak/A3-boundary-register-map-2026.10.02.svg?raw=true) | B1–B14 placed on one system picture; the full register, and what has changed since it was written |
| A4 | [Orientation and monotonicity](topak/A4-orientation-monotonicity-2026.10.02.svg?raw=true) | The orientation rule across the fourteen layers of ToO §7.8 |
| **B · Authority** | | |
| B1 | [Authority chain](topak/B1-authority-chain-2026.10.02.svg?raw=true) | From the intent axiom to an effect, and the audit chain back up |
| B2 | [Verified object and edge](topak/B2-verified-object-and-edge-2026.10.02.svg?raw=true) | What is proved once, against what may only subtract (B4); the seventeen floor policies |
| B3 | [Floor change routing](topak/B3-floor-change-routing-2026.10.02.svg?raw=true) | The computed route for a floor change and the proof-carrying gate |
| B4 | [Rules floor](topak/B4-rules-floor-2026.10.02.svg?raw=true) | R1–R9, parametricity, the two non-vacuity runs, and the proof of the six properties |
| B5 | [Promotion quorum](topak/B5-promotion-quorum-2026.10.02.svg?raw=true) | Promotion as a round: gates, seats, recusal, tally, stalls |
| B6 | [Anchor custody](topak/B6-anchor-custody-2026.10.02.svg?raw=true) | The havoc issuer; the custody axis; who is at the gate |
| B7 | [Genesis to bootstrap](topak/B7-genesis-to-bootstrap-2026.10.02.svg?raw=true) | Ratification at G9, the 22 confirmation-required records, the trigger and the ceremony |
| **C · Principals and the membrane** | | |
| C1 | [Principal, seat, cell](topak/C1-principal-seat-cell-2026.10.02.svg?raw=true) | Deployment → domain → cell → seat and stage → principal → lease |
| C2 | [Alphabets by seat](topak/C2-alphabets-by-seat-2026.10.02.svg?raw=true) | Nine variants in two domains against three seat kinds |
| C3 | [Lease anatomy](topak/C3-lease-anatomy-2026.10.02.svg?raw=true) | The twelve fields and the lease's life cycle |
| C4 | [Confinement rungs](topak/C4-confinement-rungs-2026.10.02.svg?raw=true) | Rungs 0–3, P1–P7, verdicts, and the four conjuncts of `Contained` |
| C5 | [Rung-1 launcher channel](topak/C5-rung1-launcher-channel-2026.10.02.svg?raw=true) | Launch, appraise, grant, bridge (ADR-0036, Proposed; built at the reference, ADR-0033 A7 pending) |
| **D · Admit path and the record** | | |
| D1 | [Admit pipeline](topak/D1-admit-pipeline-2026.10.02.svg?raw=true) | Decide, then order, then effect, with a denial lane |
| D2 | [Policy composition](topak/D2-policy-composition-2026.10.02.svg?raw=true) | `admit ⟺ floor_permit ∧ ¬bundle_deny`, tier by tier |
| D3 | [Record planes](topak/D3-record-planes-2026.10.02.svg?raw=true) | Log, transport, archive and payload store; round topics; erasure |
| D4 | [Privileged paths and forensic floor](topak/D4-privileged-paths-forensic-floor-2026.10.02.svg?raw=true) | Break-glass and erasure as floor exceptions; NC-1, NC-2; F1–F6 |
| **E · Detection** | | |
| E1 | [Observer topology](topak/E1-observer-topology-2026.10.02.svg?raw=true) | Cell Observers, the correlator, `W(p)` as the ACL, placement |
| E2 | [Liveness coupling](topak/E2-liveness-coupling-2026.10.02.svg?raw=true) | `live(o)`, the `K` window, the clock model and the timing budget |
| **F · Model** | | |
| F1 | [Persona, lift and lineage](topak/F1-persona-lift-lineage-2026.10.02.svg?raw=true) | The Persona, the split lift, and the lineage projection |
| **G · Trust and variation** | | |
| G1 | [Trusted base](topak/G1-trusted-base-2026.10.02.svg?raw=true) | The admission rule and all thirty-one rows, with the reference's declaration |
| G2 | [Deployment lattice](topak/G2-deployment-lattice-2026.10.02.svg?raw=true) | The archetype as unique maximum; every axis and declared degeneracy |
| G3 | [Theorem–premise DAG](topak/G3-theorem-premise-dag-2026.10.02.svg?raw=true) | All 43 binding rows as chains, an incidence matrix and the full table, with the proof column and the 2026.10.02 corrections |
| **H · Corpus and implementation** | | |
| H1 | [Corpus structure](topak/H1-corpus-structure-2026.10.02.svg?raw=true) | Layers, precedence, the checkpoint chain, and how a change moves |
| H2 | [ADR map](topak/H2-adr-map-2026.10.02.svg?raw=true) | Every record by area, with status, markers, dependencies and reversals |
| H3 | [Verification map](topak/H3-verification-map-2026.10.02.svg?raw=true) | Every check and proof, what must fail, and what neither claims |
| H4 | [Reference deployment](topak/H4-reference-deployment-2026.10.02.svg?raw=true) | The reference as deployed in development, and what is not built |
| H5 | [Proof anatomy](topak/H5-proof-anatomy-2026.10.02.svg?raw=true) | How a proof is built and kept in step: one proof module part by part, the four shapes the inductive invariants took, and the sync loop (ADR-0046; `spec/proof-method.md`) |

### Regenerating

```sh
python3 diagrams/gen-topak-family.py          # all diagrams
python3 diagrams/gen-topak-family.py B5 G3    # some
```

The generator uses only the Python standard library. Each diagram is one module in `topak/src/`. Text is
measured with tracked font metrics and wrapped, so layouts are computed rather than hand-placed. The run prints
a warning for any overlapping text or partially overlapping block; a diagram is finished when it prints none.
G3 reads `spec/theorem-premise-binding.md` at build time, and the build fails if the table no longer matches
what the module expects. See [`topak/src/AUTHORING.md`](topak/src/AUTHORING.md) for the content rules and the
visual language.

## Earlier diagrams

| Diagram | Generator |
|---|---|
| [G1 → source control → bootstrap (2026.09.18)](g1-to-bootstrap-2026.09.18.svg?raw=true) | [`gen-g1-to-bootstrap.py`](gen-g1-to-bootstrap.py) |
