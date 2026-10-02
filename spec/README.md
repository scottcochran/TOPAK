# Specifications

TLA+ modules checked in TLC at small constants, each with the mutations that must fail and the reachability
witnesses that must be violated. **They are evidence, not proofs** (every checkpoint's §8). A module cited by digest
in an accepted record is frozen; a change is a successor module (`RulesFloorNV_rev5`, `Lease_A1`). Results files are
hand-assembled TLC output with a dated name and never change; the two generators regenerate one from a row list.
`tools/tla2tools.jar` is the checker, tracked for its digest, which results files print from 2026.09.30 on.

One module has a TLAPS proof. `Anchor_proof.tla` (2026.10.02) extends `Anchor.tla` without editing it and proves
its two invariants for every floor subset and every epoch bound, with the TLA+ Proof System: `tools/tlapm` wraps the
prover `tools/install-tlaps.sh` installs (not tracked), and the proof results file prints the prover's binary
digest beside the modules'. A proof is bounded by its assumptions and the prover rather than by constants, so it
is a different kind of evidence from a TLC row; the mutation and the reachability witness stay with TLC. No record
cites the proof yet, and the checkpoints' §8 still describe the formal layer as TLC-checked.

| Module | Record | Driver | Results | Cited by digest in |
|---|---|---|---|---|
| `RulesFloorBase.tla`, `RulesFloorNV.tla` | ADR-0026 §6 | `RulesFloorNV-run.sh` | `RulesFloorNV-results-2026.09.15.txt` | ADR-0026 |
| `RulesFloorNV_rev5.tla` | ADR-0026 R1; ADR-0024 rev 5 | `RulesFloorNV_rev5-run.sh` | `RulesFloorNV-rev5-results-2026.09.23.txt` | ADR-0026, ADR-0033 |
| `NonComposition.tla` | ADR-0013 §4 | `NonComposition-run.sh` | `NonComposition-results-2026.09.23.txt` | ADR-0013 |
| `Anchor.tla`, `BreakGlass.tla` | ADR-0029 §5 (two of the five bootstrap modules) | `bootstrap-run.sh` | `bootstrap-results-2026.09.23.txt` | ADR-0029 |
| `Anchor_proof.tla` | ADR-0029 §5 (`FloorPreserved`, `EpochMonotone`), proved in TLAPS over `Anchor.tla` | `anchor-proof-results.sh` | `Anchor-proof-results-2026.10.02.txt` | Not yet cited |
| `Lease.tla` | ADR-0031 §8 | `lease-run.sh` | `Lease-results-2026.09.23.txt`, `-25.txt` | ADR-0031 |
| `Lease_A1.tla` | ADR-0031 A1 | `Lease_A1-run.sh` | `Lease_A1-results-2026.09.28.txt` | ADR-0031 |
| `FloorComposition.tla`, `FloorRouting.tla` | ADR-0030 §9 | `floor-run.sh` | `FloorComposition-results-2026.09.24.txt` | ADR-0030, ADR-0033 |
| `Confinement.tla` | ADR-0034 §7, A1 | `confinement-run.sh`; `confinement-gen-results.sh` with a row list | `Confinement-results-2026.09.25.txt`, `-28.txt`, `-30.txt` | ADR-0034 |
| `Seats.tla` | ADR-0037 §9 | `seats-run.sh` | `Seats-results-2026.09.29.txt` | ADR-0037 |
| `Observers.tla` | ADR-0038 §8 | `observers-run.sh` | `Observers-results-2026.09.29.txt` | ADR-0038 |
| `Coupling.tla` | ADR-0039 §8 | `coupling-run.sh` | `Coupling-results-2026.09.29.txt` | ADR-0039 |
| `RunCoupling.tla` | ADR-0042 §8 | `runcoupling-run.sh` | `RunCoupling-results-2026.09.29.txt` | ADR-0042 |
| `RunSeats.tla` | ADR-0043 §8 | `runseats-run.sh` | `RunSeats-results-2026.09.29.txt` | ADR-0043 |
| `Mechanism.tla` | ADR-0045 T-0045-28; ADR-0033 A5 | `mechanism-trace-run.sh` on traces the reference records; `mechanism-trace-results.sh` regenerates the file; `trace2tla.py` converts | `Mechanism-trace-results-2026.09.30.txt`, `-2026.10.01.txt` | Pinned, not frozen: the operational model moves with the code |

**`theorem-premise-binding.md`** is the table ADR-0045 §3 owes: for every property above, the trusted-base rows,
degeneracy parameters and declared gaps it rests on, with the reference's inventory computed in its last column.

Every `*-run.sh` finds the jar at `../tools/tla2tools.jar` or `$TLA_JAR`; from `spec/` no export is needed. TLC
writes its metadata under `/tmp/tlc_<name>`. `anchor-proof-results.sh` finds the prover through `tools/tlapm`
(`$TLAPM` overrides the binary) and removes its proof cache when it finishes.
