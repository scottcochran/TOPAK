# Genesis policy floor — draft

**2026.09.24** · DRAFT · not ratified · the reference instantiation ADR-0030 names (Proposed)

| File | What it is |
|---|---|
| `genesis.cedarschema` | Schema S: the typed lift's type. The analyses quantify over it (ADR-0030 §4) |
| `genesis-floor.cedar` | The floor: 14 policies — six Build envelopes, three carve-outs, two provisional Run envelopes, two exceptions, the forensic floor |
| `gen-tests.py` → `genesis-tests.json` | 38 behavioral cases; every permit allows and denies, every forbid is the reason for some deny |
| `run-gates.py` | ADR-0030 §5 gates with SymCC: totality, non-vacuity, discrimination, every-entry-matters, routing, and negative controls |
| `genesis-gates-results-2026.09.24.txt` | The gate run, with the floor and schema digests it applies to |

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
- **Invoke hermeticity** is not in the floor; it is an obligation on each allowlist entry (ADR-0022 §3).
