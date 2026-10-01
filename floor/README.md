# Genesis policy floor — draft

**2026.09.24**, revised 2026.09.30 · DRAFT · not ratified · the reference instantiation ADR-0030 names

| File | What it is |
|---|---|
| `genesis.cedarschema` | Schema S: the typed lift's type. The analyses quantify over it (ADR-0030 §4) |
| `genesis-floor.cedar` | The floor: 17 policies — six Build envelopes, four carve-outs (B10 from ADR-0037 §4), three Run envelopes (R1, R2, R4 from ADR-0040 §1 and ADR-0041 §1), one Run carve-out (R3 from ADR-0039 §2, over effects only), two exceptions, the forensic floor |
| `gen-tests.py` → `genesis-tests.json` | 62 behavioral cases; every permit allows and denies, every forbid is the reason for some deny |
| `run-gates.py` | ADR-0030 §5 gates with SymCC: totality, non-vacuity, discrimination, every-entry-matters, routing, and negative controls. Since 2026.10.01 every solver call goes through `cvc5-checked` and the header names the checker |
| `cvc5-checked` | The solver wrapper of ADR-0030 §5 A1. `cedar symcc` runs it in place of cvc5: it keeps each query, runs cvc5 with proof production, binds the proof to the query's own declarations and assertions, and forwards `unsat` only after the pinned checker (`ethos` 8dc85c4, built by `tools/install-ethos.sh`, against the CPC signature in `tools/cpc/`) accepts it; anything else is `unknown`, which cedar reports as a failure |
| `genesis-values.json` | Policy-floor **values**: the numbers the typed lift reads that Cedar text cannot hold (`K`, `T_obs`; ADR-0035's θ, unset). Part of the floor bundle; its digest is recorded with the floor's and the schema's (ADR-0039 §1). **Placeholders, not ratified, not measured** |
| `genesis-gates-results-2026.09.24.txt` | The gate run of 09.24, before ADR-0037 |
| `genesis-gates-results-2026.09.29.txt` | The gate run after ADR-0037 §4: `Seat.kind` in S, B6 tightened, B10 added. All gates pass; 47/47 cases |
| `genesis-gates-results-2026.09.29-adr0039.txt` | The gate run after ADR-0039 §2: `observerLive` in RunCtx, R3-observer-live (Thinker seats only), the values file digested with the bundle. All gates pass; 51/51 cases |
| `genesis-gates-results-2026.09.29-adr0041.txt` | The gate run after ADR-0040 and ADR-0041 (both Proposed): `Consult`, `Actuate` and `Report` in S, `runRoot` in RunCtx, R4-consult-pinned added, R3 over effects only. All gates pass; 62/62 cases; two controls added. **These are the digests the mechanism pins** |
| `genesis-gates-results-2026.09.30.txt` | The gate run after ADR-0031 A2 (Pending): `persona.T_persona_ms` joins the values file, so its digest moves. Floor and schema unchanged; every gate result identical to the 09.29-adr0041 run |
| `genesis-gates-results-2026.10.01.txt` | The first **proof-carrying** run (ADR-0030 A1, Batch 24). Floor, schema and values unchanged from 09.30. 81 cedar calls, 56 solver queries: 4 `unsat` each with a proof the checker accepted (`holds✓`), 49 `sat`, 3 `unknown` from the three lying-solver controls; 25 `holds°` cedar decided without a solver query (never-errors, and a permit-all under always-allows). Every run before it is a D-0030-2 run |
| `genesis-gates-evidence-2026.10.01/` | That run's evidence: per cedar call, the query (`q-N.smt2`), the bound proof (`q-N.cpc`) and the verdict (`q-N.json`, with the query, proof, solver and checker digests); `index.tsv` maps calls to analyses. Tree digest `f8b1196a427a35ed`, printed at the end of the results and reproducible run to run |

## Running

```sh
cargo install cedar-policy-cli --features analyze     # `symcc` is behind this feature
export CVC5=/path/to/cvc5                             # cvc5 1.4.0 static build used for the recorded run
../tools/install-ethos.sh                             # the pinned proof checker, once; ETHOS=... overrides its path

cedar validate  --schema genesis.cedarschema --policies genesis-floor.cedar
python3 gen-tests.py
cedar run-tests --schema genesis.cedarschema --policies genesis-floor.cedar --tests genesis-tests.json
python3 run-gates.py genesis-gates-results-<date>.txt
```

## What is provisional

- **Run's alphabet is ADR-0040 §1's, and the six Run entries are ADR-0041 §1's**, both ratified 2026.09.30 (Batch
  20). The floor itself is still DRAFT, as ADR-0030 left it. `RunInvoke` and `RunEmit` are retired: a request naming
  either fails validation against S, and any error is a deny.
- **`Consult` is not coupled to the Observer**, and the exemption rests on R4's pinning (ADR-0041 §2). The gate run
  carries two controls for it: a permit-all on `Consult` is caught by non-vacuity, and R4 without its Run-root
  conjunct is classed a relaxation by routing. **The second is not caught by non-vacuity**, because the domain
  and alphabet conjuncts still refuse requests; ADR-0041 §7 names the wrong gate for it.
- **One policy set for two domains.** Policies are scoped by `principal.domain` because the per-class floor question
  (ToO §3.4) is open. Splitting later changes the files, not the entries.
- **Every number in `genesis-values.json` is a placeholder.** `K = 8` and `T_obs = 5000 ms` were chosen on
  2026.09.29 so the ADR-0039 ratification run has values; they are deployment and rung choices, declared per
  deployment, not the pattern's values. The θ values are unset until measured (G4 item 30). `T_persona = 1 h` was
  added on 2026.09.30 for ADR-0031 A2 (Pending) and is not yet read by the reference. The round bound `R` is
  **not** here: it is a mechanism parameter (ADR-0022 §3, `mechanism/` I21), set per domain in the mechanism's
  configuration, and the mechanism checks `K < R` for each domain at startup.
- **Invoke hermeticity** is not in the floor; it is an obligation on each allowlist entry (ADR-0022 §3).
- **What the checker does not cover.** A `holds°` is cedar's own term folding, with no solver query to check; it
  rests on the engine's row (ADR-0045 T-0045-3). The checker's rule signature (`tools/cpc/`) is trusted as written
  by cvc5's authors; a wrong rule there is the residual ADR-0045 T-0045-14 states.
