# In the TOPAK repository

Everything else in this skill is general. This file names the corpus's own paths and records.

## Packages

| Package | States | Root | Builds |
|---|---|---|---|
| `spec/lean/` | Re-encodings of `spec/*.tla`, mirrors | `TopakSpec` | ~10 s, core Lean only |
| `mechanism/lean/` | Transcriptions and models of `mechanism/crates/` | `Topak` | Depends on `spec/lean` by path |
| `floor/lean/` | The floor under cedar-spec (`gen.py` generates) | `TopakFloor` | cedar-spec v4.13.0, batteries; first build is long |

Each package's README has the theorem tables, encoding notes and mutant tables. Add new rows there.

## Tools

| Purpose | Where |
|---|---|
| Pin | `tools/LEAN-PIN`; `tools/install-lean.sh` installs and compares |
| Build and replay half of a results file | `tools/lean-report.sh <pkg> <root>` |
| Sync | `tools/lean-sync.sh` |
| Results | `spec/lean/results.sh > TopakSpec-results-<date>.txt`, and the same in `mechanism/lean` (`Admit-`) and `floor/lean` (`TopakFloor-`) |
| State graph check | `spec/lean/graph-check.sh`, `graph-check-emergency.sh` |
| Trace replay | `mechanism/lean/seats-replay.sh`, `coupling-replay.sh` |

Adding a re-encoded module means adding it to `tla` and `modules` in `spec/lean/results.sh`, to `spec/lean/TopakSpec.lean`,
and to the theorem pattern in `results.sh` if its theorems don't end in `Always`.

What a new encoding moves besides that. Report these; each has an owner:

- `spec/specification-graph.json` holds the digest of `TopakSpec.lean` in sixteen places, so editing the root import
  makes those edges stale. `build --repin <ids>` is the review, so leave it, and the new encoding's own edge is not
  added for you.
- The count of encoded modules, "sixteen", is in `README.md`, `spec/README.md`, `spec/lean/README.md`, and diagrams H1, H3
  and H7.
- ADR-0053's list of modules not yet encoded is record text, so it changes only by a record act.
- `spec/theorem-premise-binding` gains no premise for the new encoding unless someone adds one.

## Records

- ADR-0053 is the method; §1 the three uses, §2 what a result claims, §4 citing by digest, §5 the premise table's
  Lean route. Changing what a result claims or which results file it cites needs a record change, which is
  the `ratifying-records` procedure when ratified text moves.
- T-0045-37 is the toolchain's trusted-base row. Moving the pin is a change every results file shows.
- `spec/proof-method.md` §5b has the assessment; §4 the TLAPS habits.
- Word: **proved in Lean**, never "proved" alone (ADR-0053 §1). ADR-0046 §1 reserves "proved" for TLAPS.
- `spec/theorem-premise-binding.*` reads `enc-faithful(Seats)` and `enc-faithful(FloorComposition)` from the newest
  `GraphCheck-results-*.txt`, so editing a shared file (`Prelude.lean`, `GraphCheckCore.lean`, `dot2lines.py`) stales
  those premises.
- A floor stage switch (`topak-floor` `include_str!`) needs `floor/lean/gen.py <stage>` and a `Linked.lean`, named after
  `linked:` on the results file's `Floor:` line, or `lean-sync.sh` fails.
- Adding an `ActionKind` or `SeatKind` leaves `mechanism/lean`'s models stale.
- tlapm 7824dab has two known unsound cases. `writing-tla-specs-and-proofs` has the rules and the scan. A Lean proof is
  a route around them for a step in doubt, with its own premise.

## Known state

Check with `tools/lean-sync.sh`, because this moves. At 2026.11.10 `spec/lean` and `floor/lean` were in sync, and
`mechanism/lean` and its two replays were stale: `state.rs`, `trace.rs`, `mechanism.rs` and `topak-floor`'s `lib.rs`
have moved since 2026.10.06 and the custodian chose to leave it so (GAPS I49). Regenerating the `Admit` series without
re-reading those re-blesses them, and removes the stale marking that names that debt.

The worktree has no `tools/` binaries, but Lean comes from `~/.elan` and needs none of them.
