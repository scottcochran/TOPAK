# TOPAK — Recovery registry

**2026.09.15** · all 48 conversations in the TOPAK Project scrubbed (2026.09.09 – 2026.09.15) · cleanup step 2 · **tranche 3 complete; step 2 closed**

**Recovery rule.** Each record is recovered from its **last authoritative text** in session history.
It is recovered verbatim and **unfolded**: later amendments stay in `pending/`. Recovered files carry
a header naming their source session and turns.

## 1. Decisions (ADRs)

| # | State | Source | Tranche |
|---|---|---|---|
| 0001 | **Recovered** | 09.11 checkpoint §9 + ADR review turns 3, 5, 9 | 1 ✓ |
| 0002 | **Recovered** — finding: no evictability test in the text; A1 struck text absent | 09.11 checkpoint + review turns 1, 3 | 1 ✓ |
| 0003 | **Recovered** — finding: sealing certificate, Merkle root, and opaque naming designed but not recorded | 09.11 checkpoint | 1 ✓ |
| 0004 | **Recovered** — finding: "rationale unrecorded" is wrong | 09.11 checkpoint + review turns 41, 43 | 1 ✓ |
| 0005 | **Recovered** | 09.11 checkpoint + review turns 49–50 | 1 ✓ |
| 0006 | **Recovered** | 09.11 checkpoint + review turns 27, 31 | 1 ✓ |
| 0007 | **Recovered** — finding: no §4.2 citation | 09.11 checkpoint + review turns 5, 9, 23 | 1 ✓ |
| 0008 | **Recovered** | 09.11 checkpoint + review turns 11, 37 | 1 ✓ |
| 0009 | **Recovered** | 09.11 checkpoint + review turns 27, 31 | 1 ✓ |
| 0010 | **Recovered** — A1 struck text confirmed | Review turns 23, 25 | 1 ✓ |
| 0011 | **Recovered** (tombstone) | Review turn 39 | 1 ✓ |
| 0012 | **Recovered** | Review turn 25 | 1 ✓ |
| 0013 | On disk (09.15 draft skeleton) | This session | — |
| 0014 | No text exists | — | — |
| 0015 | **Recovered** (09.12 base; 09.15 revision in `pending/`) | Review, final draft | 1 ✓ |
| 0016 Persona | **Recovered** by replay — finding T2-1 | [MANAGE 3.2](https://claude.ai/chat/c18ad385-6cf1-42b5-83a1-09571ad211e8) turns 7, 9, 17, 21 | 2 ✓ |
| 0017–0019 | **Recovered** by replay; split from one file — findings T2-1, T2-4 | Same session, turns 17, 21 | 2 ✓ |
| 0020 | **Recovered** | Same session, turn 21 | 2 ✓ |
| 0021 (drafted as 0016) | **Recovered** — draft number kept verbatim | [Build gaps](https://claude.ai/chat/27868293-ee93-45b4-8f75-b7ca15991733) turn 3 | 2 ✓ |
| 0022 (drafted as 0017) | **Recovered** — finding T2-3 | Build gaps turn 5 | 2 ✓ |
| 0023 | **Recovered**; clause 7 present | [Degenerate rungs](https://claude.ai/chat/4f5de952-d34a-46a5-b66d-d458bc61c34e) turn 3 | 2 ✓ |
| 0024–0029 | On disk (09.15) | This session | — |

**Tranche 2 method.** Start a fresh session with this corpus uploaded. For 0016–0020, read the
`create_file` call, then replay every later `str_replace` and Python patch in order, and diff against
the acceptance turn. Do not reconstruct from summaries.

**Tranche 2 findings** (not ratified; recorded for G1 and the fold)

- **T2-1. One Python replacement in the 0016 acceptance patch was a no-op.** Turn 21 ran
  `"This is ADR-0016 §8's concession" → "This is ADR-0020's concession"` against the 0016 file,
  but the phrase lives in 0018. So 0018 still cites **ADR-0016 §8**, and 0019 cites it three
  times (Relates to, Context, Consequences), which nothing ever targeted. All four still resolve
  through 0016's §8 stub ("Split to ADR-0020"), so nothing is broken. Candidate erratum:
  ADR-0016 §8 → ADR-0020 at those four sites.
- **T2-2. Every other edit matched exactly once.** The one turn-17 `str_replace` sent to
  `/mnt/user-data/operations/` failed in session and was repeated on the correct path; it is
  replayed once. Turn 21 wrote 0016 §9 with an `ADR-0020 [sic: ADR-0019]` placeholder and
  corrected it in the same script, so the final text is clean.
- **T2-3. The ratified 0022 erratum names the wrong locations.** Its substance (ADR-0016 →
  ADR-0021) is unaffected. The recovered text has **no** ADR-0016 in §3 or in Requires
  follow-up. It **does** have one in the header (Unblocks, Relates to), Context, the §1 prose
  after the table, and two Consequences bullets, in addition to the §1 `Emit` row. The title line
  also still reads "ADR-0017". Correct the location column at fold, as Batch A did for 0002 A2.
- **T2-4. The ratified 0017 erratum targets a "rationale" section that 0017 does not have.**
  0017 has Context, Decision, Consequences, Ratification note, and Open. Pick a home at fold
  (Context is the natural one).
- **T2-5. 0023 is an inline draft at H2 with H3 sections**, unlike the series' H1 files. Left as
  drafted; normalization is a permitted freeze step.

## 2. Other artifacts

| Artifact | Session | Kind | Recover? |
|---|---|---|---|
| Theory of Operation 09.10 | [382e85af](https://claude.ai/chat/382e85af-e7f4-4ebf-ba54-1d993e6a2c7a) | inline checkpoint | **Recovered** (`checkpoints/`), historical. Turn 1; file name assigned at recovery |
| Theory of Operation 09.11 (`topak-theory-of-operation-2026.09.11.md`) | [8e4b4455](https://claude.ai/chat/8e4b4455-6594-4d23-a77a-eae3ac70ea8e) | file | **Recovered** (`checkpoints/`), historical. No later edits |
| Theory of Operation 09.12 (`…-2026.09.12.md`) | [07876ffb](https://claude.ai/chat/07876ffb-88f6-4f95-b7db-6011f705617e) | file | **Recovered** (`checkpoints/`), historical. No later edits |
| Theory of Operation 09.15 rev 4 | this session | file | **In corpus** (`checkpoints/`) |
| Glossary 09.11 | [ac8ee1ab](https://claude.ai/chat/ac8ee1ab-9f4e-4f7f-bab8-2798b16e9498) | file | No. Stale; regenerate after G1 |
| External assessment 09.12 | [816fe6b6](https://claude.ai/chat/816fe6b6-9f6b-4f7b-ad08-06e5137d7a45) | file | **Recovered** (`derived/`), marked historical (ADR-0006 mechanism misstated; T3-3). No later edits |
| NIST Playbook delta inventory 09.12 | [94ed200e](https://claude.ai/chat/94ed200e-086a-497d-b95b-941d41531ca7) | file | **Recovered** (`derived/`), marked historical (tally error, T3-2; ADR-0006 mechanism misstated, T3-1). No later edits |
| Boundary register 09.13 (`topak-boundary-register-2026.09.13.md`) | [dc8a8875](https://claude.ai/chat/dc8a8875-0eb9-4494-94b6-aa14802085e1) | file | **Recovered** (`derived/`). No later edits |
| TLA+ Paxos cheat sheet 09.13 | [566f11d6](https://claude.ai/chat/566f11d6-b049-47b2-b826-a9450dfed8b4) | file | **Recovered** (`derived/`), reference. No later edits |
| Feature list 09.15 | this session | file | **In corpus** (`derived/`) |
| Genesis manifest v1 | this session | file | **In corpus** (`checkpoints/`) |
| `RulesFloorNV.tla` + results + runner | this session | spec | **In corpus** (`spec/`) |
| Architecture diagrams (SVG) and two PDFs | [7d8a1f1b](https://claude.ai/chat/7d8a1f1b-2df6-4bde-8ce0-c6818e1f108c), [0b1272a0](https://claude.ai/chat/0b1272a0-35bf-4493-9bfe-7344195adf75) | pre-corpus | No. They predate LTRO and Build/Run naming |
| Draft article (`TOPAK__An_Architecture_Pattern…`) | Project knowledge | file | Already in Project |

**Tranche 3 method.** Each artifact came from a single turn: five `create_file` calls and one inline
response (09.10). A history search found no later `str_replace` or patch against any of them. Two
cross-checks: the 09.11 checkpoint's §9 ADR paragraphs for 0001, 0003, 0005, 0006, 0007, and 0009
match the tranche-1 records verbatim, and an independent recount of the delta inventory's row marks
reproduces the feature list §9 correction exactly. Recovered files carry a `HISTORICAL` header:
nothing folds into them.

**Tranche 3 findings** (not ratified; recorded for G1)

- **T3-1. The delta inventory repeats the ADR-0006 misstatement.** Its MANAGE 2.4 row says
  "ADR-0006 crypto-shreds," and its MEASURE 2.10 row lists crypto-shredding as privacy machinery.
  The registry previously gave only the tally as the reason to mark it historical. The 09.15
  checkpoint §9 already names all three documents as affected, so no new correction is needed.
  The 09.12 checkpoint itself never makes the claim.
- **T3-2. The tally error is confirmed and has two knock-ons.** Row marks sum to M 6 · P 12 · C 15 ·
  G 9 · X 30 · ! 1. Besides the headline tally, the "MEASURE (19)" heading and §7's "eight G rows"
  and "fourteen C rows" follow the wrong numbers. This matches feature list §9.
- **T3-3. ADR-0028's Context misattributes a phrase.** It says the 09.12 external assessment
  observed a forensic floor "running in the opposite direction" from the policy floor. The
  assessment *file* says "monotone in the same direction (exceptions may preserve more, never
  less)." "Opposite direction" appears in that session's closing chat message (turn 3, outside the
  file) and in the delta inventory's MANAGE 2.4 row. The rule is identical in all three places;
  only the label differs. Each label is right under a different reading: both floors constrain
  change in one direction, but the policy floor caps authority (bundles may only subtract) while
  the forensic floor guarantees retention (exceptions may only preserve more). Candidate erratum:
  cite the delta inventory, or state the rule instead of the direction.
- **T3-4. The 09.10 checkpoint was never a file.** It is recovered from an inline response. Its
  lead-in sentence is omitted, and Scott's six-line prompt is quoted in the header because the body
  refers to it.

## 3. Design content with no record

Found while scrubbing. These are candidates, not recovered.

| Content | Session | Likely home |
|---|---|---|
| Sealing certificate, Merkle root over round envelopes, HMAC-base32 topic names | [8b4223ef](https://claude.ai/chat/8b4223ef-ac5c-4090-bd35-35e0d82f67d9) | 0003 clauses or a companion record |
| "Army of one" degraded mode | [a7fad171](https://claude.ai/chat/a7fad171-1773-42b8-ad96-aa9b5c3fb254) | GOVERN 6.2 record |
| DAG reversibility: compensable prefix, pivot, retriable suffix; lease TTL < compensator window | [8cdaf02d](https://claude.ai/chat/8cdaf02d-f1be-4536-aa7b-5a8b003b1857) | Unrecorded decision |
| Deadman e-stop; halt ≠ purge; e-stop clearance voids leases; `W < L < D` | [d6490a01](https://claude.ai/chat/d6490a01-0c13-470b-9e05-c64173b94ec8) | Unrecorded decisions |
| Paxos over Kafka, not KRaft; three consensus groups | [0c95e28a](https://claude.ai/chat/0c95e28a-4f08-4ed6-96b0-f3609e452c8a) | Unrecorded decisions |
| Signed message format analysis (protobuf/CBOR, sign received bytes) | [711cd4f7](https://claude.ai/chat/711cd4f7-340e-4a1c-9648-c99581916ea5) | Genesis-blocking open decision |
| Policy within an epoch, boundary between epochs; Rust sidecar, OPA sidecar; repo layout | [cadc11aa](https://claude.ai/chat/cadc11aa-4c95-4472-a224-851544516871) | Unrecorded decisions |
| Bundle deployment modes (forcing / eventual / decomposed) | [7d8a1f1b](https://claude.ai/chat/7d8a1f1b-2df6-4bde-8ce0-c6818e1f108c) | Unrecorded decision; may predate the floor model |

**These matter for genesis.** Several were stated as decisions in session but never became ADRs.
Under ADR-0029 they are not genesis content until recorded. G1 should list them as known unrecorded
decisions, so a future reader doesn't take their absence to mean they were rejected.
