# The small spec/ modules in Lean 4

Seven TLA+ modules of `spec/`, re-encoded as transition systems in Lean 4 and their TLAPS theorems proved by
induction on reachable states: `Seats`, `Observers`, `RunSeats`, `FloorRouting`, `NonComposition`, `Anchor`
and `BreakGlass`, with `RulesFloorBase` as the last two's shared base. Each `TopakSpec/<Module>.lean` carries
the TLA+ it transcribes beside every definition and proves what `spec/<Module>_proof.tla` proves, with the
same inductive invariants and the same hypotheses on `Mut`.

## What this adds to the TLAPS proofs

`spec/proof-method.md` §5a: in the certified run, every obligation is closed by tlapm's normalization, by a
checked SMT proof, or by **LS4** for the temporal step of each theorem, "the invariant holds initially, every
step keeps it, so it holds always", which is checked by nothing. Here that step is `Prelude.invariant`,
an induction on `Reachable`, and the kernel checks it. The Lean theorems are therefore the TLAPS theorems with
the LS4 premise removed and a different one added: that the Lean encoding is the TLA+ module.

Three of the TLAPS proofs' assumptions vanish under Lean's types. `TypeOK` lemmas have no counterpart.
`Active ⊆ AllEntries` (Anchor, BreakGlass) holds because `Active` is a set of entry names. `MaxEpoch ∈ Nat`
holds because `MaxEpoch : Nat`. One stays: BreakGlass's `"R7" ∈ Active` is the hypothesis `hR7`, as it must
be, since the property is R7's claim.

## Theorems

| File | Theorems | Hypotheses |
|---|---|---|
| `Seats.lean` | `OnlyThinkersAuthorAlways`, `OneSeatPerPrincipalAlways`, `SafeAlways` | `m ≠ M_KIND`; `m ≠ M_SEAT`; `none` |
| `Observers.lean` | `DenyByAnyOfAlways`, `ReachIsBoundedAlways`, `SafeAlways` | `m ≠ M_QUORUM`; `m ≠ M_REACH`; `none` |
| `RunSeats.lean` | `OnlyThinkersActuateAlways`, `ObserversConsultAndReportAlways`, `NoNameCrossesDomainsAlways`, `SafeAlways`, `SafeUnderObsEmit` | `m ≠ M_KIND`; `m ≠ M_KIND`, `m ≠ M_DOMAIN`; `m ≠ M_DOMAIN`; `none`; `M_OBSEMIT` |
| `FloorRouting.lean` | `SafeAlways`, `NoWideningAlways`, `NeverVacuousAlways` | `none` |
| `NonComposition.lean` | `SafeAlways`, `NC1Always`, `NC2Always` | `m ≠ M1`, `m ≠ M2` |
| `Anchor.lean` | `FloorPreservedAlways`, `EpochMonotoneAlways` | `none`; any `m` |
| `BreakGlass.lean` | `NeverChangesAuthority` | `none`, `R7 ∈ Active` |
| `RulesFloorBase.lean` | `GenesisEntries`, `GenesisFloor` | the module's `ASSUME`, proved |

Each file also carries the TLAPS module's "why the mutation must fail" lemmas where they are about the
definitions rather than about a TLC run. Witnesses stay with TLC.

## How the TLA+ is encoded

`TopakSpec/Prelude.lean` states the conventions. A TLA+ set is a predicate; a string-valued constant set is an
inductive type; a BOOLEAN variable is a `Prop` and `x' = (a \/ b)` is `x' ↔ a ∨ b`; `IF` on a decidable
condition is `if`, on a set membership it is a pair of implications; `S # {}` is `NonEmpty S`;
`Cardinality` is the relation `HasCard`; stuttering steps are dropped. Two renamings: the TLA+ action
`Act(s)` is `ActStep` where `Act` names the set of acts, and `Finding(o, t)` is `FindingStep` where
`Finding` names the record.

## What it rests on

- **The Lean 4 kernel**, toolchain `lean-toolchain` (v4.24.0). No Mathlib, no dependencies. `#print axioms`:
  `propext` and `Quot.sound` at most for six modules; `NonComposition` also uses `Classical.choice`, because
  its `Erase` step cases on a set membership, as TLA+ does. No `sorry`. Lean is not yet a trusted-base row.
- **The encoding.** A proof here is of the Lean re-encoding, not of the frozen TLA+ text, which the TLAPS
  proofs are of. The encoding is written from the module and read against it; `derived/lean.md` names this
  as the new premise. Where the encoding could be read two ways, the file says which was taken.

## Mutation check

Nine mutated copies of the encodings were built on 2026.10.05, each a spec mutation with its `Mut` guard
removed or a finite table widened. Each fails to build, in the lemma that carries the mutated definition
into the inductive step; the theorems proved through that lemma then rest on `sorryAx`.

| Module | Mutant | Fails in |
|---|---|---|
| Seats | the observer kind bound includes `Draft` | `KindBoundKinds` (feeds `OnlyThinkersAuthorAlways`) |
| Seats | the grant ignores `HoldsElsewhere` (M_SEAT always) | `NextInvS` (feeds `OneSeatPerPrincipalAlways`) |
| Observers | every observer reaches every thinker (M_REACH always) | `NextReach` (feeds `ReachIsBoundedAlways`) |
| Observers | the quorum rule under every `Mut` (M_QUORUM always) | `NextDeny` (feeds `DenyByAnyOfAlways`) |
| FloorRouting | every proposal routes to promotion | `PromoteNarrows` (feeds `NoWideningAlways`) |
| RunSeats | the observer kind bound includes `Actuate` | `KindActuate`, `ObserverRun` |
| NonComposition | F1 is erasable under `none` (M1 always) | `ForensicKept` (feeds `NC2Always`) |
| BreakGlass | the envelope is ignored (M_SCOPE always) | `NextInv` (feeds `NeverChangesAuthority`) |
| Anchor | the floor check is omitted (M_FLOOR always) | `NextFloor` (feeds `FloorPreservedAlways`) |

## Run it

```sh
cd spec/lean
lake build                                        # the proofs; ~3 s
./results.sh > TopakSpec-results-<date>.txt       # clean build, with the digests of the TLA+ modules, the Lean sources and the toolchain
```

`TopakSpec-results-2026.10.05.txt` is the first results file. Its `Transcribes:` line binds each Lean file to
the digest of the TLA+ module it encodes, as a TLAPS results file's `Modules:` line does; when a module gets a
successor, the successor's encoding is a new file.
