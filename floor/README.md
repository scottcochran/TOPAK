# Genesis policy floor — draft

**2026.09.24** · DRAFT · not ratified · the reference instantiation ADR-0030 names (Proposed)

| File | What it is |
|---|---|
| `genesis.cedarschema` | Schema S: the typed lift's type. The analyses quantify over it (ADR-0030 §4) |
| `genesis-floor.cedar` | The floor: 16 policies — six Build envelopes, four carve-outs (B10 from ADR-0037 §4), one Run carve-out (R3 from ADR-0039 §2), two provisional Run envelopes, two exceptions, the forensic floor |
| `gen-tests.py` → `genesis-tests.json` | 51 behavioral cases; every permit allows and denies, every forbid is the reason for some deny |
| `run-gates.py` | ADR-0030 §5 gates with SymCC: totality, non-vacuity, discrimination, every-entry-matters, routing, and negative controls |
| `genesis-values.json` | Policy-floor **values**: the numbers the typed lift reads that Cedar text cannot hold (`K`, `T_obs`; ADR-0035's θ, unset). Part of the floor bundle; its digest is recorded with the floor's and the schema's (ADR-0039 §1). **Placeholders, not ratified, not measured** |
| `genesis-gates-results-2026.09.24.txt` | The gate run of 09.24, before ADR-0037 |
| `genesis-gates-results-2026.09.29.txt` | The gate run after ADR-0037 §4: `Seat.kind` in S, B6 tightened, B10 added. All gates pass; 47/47 cases |
| `genesis-gates-results-2026.09.29-adr0039.txt` | The gate run after ADR-0039 §2: `observerLive` in RunCtx, R3-observer-live (Thinker seats only), the values file digested with the bundle. All gates pass; 51/51 cases. **These are the digests the mechanism pins** |

## Running

```sh
cargo install cedar-policy-cli --features analyze     # `symcc` is behind this feature
export CVC5=/path/to/cvc5                             # cvc5 1.4.0 static build used for the recorded run

cedar validate  --schema genesis.cedarschema --policies genesis-floor.cedar
python3 gen-tests.py
cedar run-tests --schema genesis.cedarschema --policies genesis-floor.cedar --tests genesis-tests.json
python3 run-gates.py genesis-gates-results-<date>.txt
```

## What is provisional

- **Run's alphabet.** No record defines it. `RunInvoke` and `RunEmit` carry ADR-0015's two Run effects until one
  does, and break-glass's envelope is stated over `RunInvoke`.
- **One policy set for two domains.** Policies are scoped by `principal.domain` because the per-class floor question
  (ToO §3.4) is open. Splitting later changes the files, not the entries.
- **Every number in `genesis-values.json` is a placeholder.** `K = 8` and `T_obs = 5000 ms` were chosen on
  2026.09.29 so the ADR-0039 ratification run has values; they are deployment and rung choices, declared per
  deployment, not the pattern's values. The θ values are unset until measured (G4 item 30). The round bound `R` is
  **not** here: it is a mechanism parameter (ADR-0022 §3, `mechanism/` I21), set per domain in the mechanism's
  configuration, and the mechanism checks `K < R` for each domain at startup.
- **Invoke hermeticity** is not in the floor; it is an obligation on each allowlist entry (ADR-0022 §3).
