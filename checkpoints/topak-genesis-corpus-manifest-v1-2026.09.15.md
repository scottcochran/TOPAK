# TOPAK — Genesis corpus manifest v1

**2026.09.15** · genesis custody: Scott, sole, (1, 0) · governed by ADR-0029 revision 2 (**Accepted (genesis)** 09.15) · *The Gripping Hand*

This is a snapshot of the whole corpus in its current state, drafts included. **It ratifies
nothing.** Ratification is a separate act by the custodian. At bootstrap, the manifest current at
that moment becomes part of the genesis bundle.

**Digest.** Truncated SHA-256 (first 16 hex characters) of the file as it exists this session.
"not on disk" means the record lives only in session history; recover it into files before
bootstrap.

**Readiness key**

| Code | Meaning |
|---|---|
| **R** | Ratifiable now: decision text exists |
| **R·CR** | Ratifiable; confirmation required on ratification (ADR-0029 §4) |
| **N** | Not ratifiable: no decision text |
| **BS** | Bootstrap set: cannot be confirmation-required |
| **—** | Already accepted, or tombstone |

---

## 1. Records

| # | Title | Status | Readiness | File · digest |
|---|---|---|---|---|
| 0001 | Rename CI domain to `Build` | Accepted | — | not on disk |
| 0002 | Apply `Contain` in Build as well | Accepted · A1, A2 drafted | A1, A2: **R** | not on disk · amendments file |
| 0003 | Topic per principal per epoch/round | Accepted · clauses annotated (drafted) | annotation: **R** | not on disk · amendments file |
| 0004 | Separate control-plane facts from cognitive payloads | Accepted · rationale unrecorded | — | not on disk |
| 0005 | Kafka is neither ordering authority nor system of record | Held | **R** (Observer-gate debt) | not on disk |
| 0006 | Erasure is a modeled event | Accepted · debt to 0013 · **confirmation required** | — | not on disk |
| 0007 | Semantic judgment is never a lift | Accepted · erratum drafted | erratum: **R** | not on disk · amendments file |
| 0008 | Observer replicas not colocated with the Thinker | Accepted · reversed in effect | — (supersession: **N**, CR when written) | not on disk |
| 0009 | Break-glass is modeled, quorum-witnessed | Accepted · debt to 0013 · **confirmation required** | — | not on disk |
| 0010 | Verified object = mechanism + minimal policy floor | Accepted · A1, A2, erratum drafted | **R** · BS (via 0026) | not on disk · amendments file |
| 0011 | Observer placement | Tombstone | — | — |
| 0012 | Default-deny bundle is the policy floor | Accepted | — | not on disk |
| 0013 | Exception mechanism for privileged paths | Draft skeleton | **N** (CR when written) | topak-adr-0013-2026.09.15.md · `8af8718a45803222` |
| 0014 | Floor authorship and change control | Open | **N** | — |
| 0015 | Boundary effects audit | Proposed · revised | **R·CR** (C2) | not on disk (09.12) · pending-revisions file |
| 0016 | Persona | Accepted | — | not on disk |
| 0017 | Archetype admits only in-house pre-trained Personas | Accepted · erratum drafted · ordering clause reversed in effect | erratum: **R** (supersession: **N**, CR) | not on disk · amendments file |
| 0018 | Typed lift splits | Accepted | — | not on disk |
| 0019 | Optional decode observability (narrow) | Accepted | — | not on disk |
| 0020 | Replay scope is boundary events only | Accepted | — | not on disk |
| 0021 | Build effect stream | Proposed | **R** | not on disk (drafted as 0016) |
| 0022 | Build action alphabet | Proposed · revised · errata | §1–5, §7, §8: **R** · BS · §6: **R·CR** (C2) | not on disk (drafted as 0017) · pending-revisions file |
| 0023 | Degeneracy as the deployment-variation relation | Proposed · scope carried | decision: **R** · carried scope: **N** | not on disk · pending-revisions file |
| 0024 | Promotion requires a quorum | Proposed rev. 4 | **R** · BS | topak-adr-0024-2026.09.15.md · `2fd6720e1dc551fc` |
| 0025 | Trust anchor is a havoc issuer | Proposed rev. 3 | **R** · BS | topak-adr-0025-2026.09.15.md · `b61fefd5c5061752` |
| 0026 | The rules floor | Proposed rev. 2 · non-vacuity passed · R4 withdrawn | R1–R3, R5, R7: **R** · BS · R6, R8: **N** | topak-adr-0026-2026.09.15.md · `3ea920ce9e622176` |
| 0027 | Genesis rules are resident | Proposed | **R** · BS | topak-adr-0027-2026.09.15.md · `afb9db9e3a43e378` |
| 0028 | Forensic floor | Proposed | **R·CR** (C1) | topak-adr-0028-2026.09.15.md · `32b59b07e41a2779` |
| 0029 | Genesis; unilateral ratification; bootstrap | **Accepted (genesis)** 09.15 | — | topak-adr-0029-2026.09.15.md · `256ddb3045533a8a` |

## 2. Declaration records

| Record | Kind | Parent | Status |
|---|---|---|---|
| A-0025 | Archetype custody (n, 0) | 0025 annex | Drafted |
| D-0025-1 | TUF-style threshold (k, n−k) | 0025 annex | Drafted |
| D-0025-2 | n−1 eviction with replacement (n−1, 1) | 0025 annex | Drafted |
| D-0024-1 | k-of-n promotion (rules-floor change to R1) | 0024 | Drafted |
| D-0024-2 | Single signer (rules-floor change to R1) | 0024 | Drafted |
| — | Provenance, legibility, and Observer-scoping demotions | 0023 | Not written |

## 3. Supporting documents

| Document | File · digest |
|---|---|
| Theory of Operation checkpoint 2026.09.15 rev. 4 | topak-theory-of-operation-2026.09.15.md · `b1a740bce9534268` |
| Amendments and errata to accepted ADRs | topak-adr-amendments-accepted-2026.09.15.md · `a59a6638a14c3a28` |
| Revisions to pending ADRs | topak-adr-pending-revisions-2026.09.15.md · `0d4811bebbf823ea` |
| Feature list | topak-feature-list-2026.09.15.md · `514f3ca733bbc886` |
| Non-vacuity spec (genesis artifact) | RulesFloorNV.tla · `1468d8bab89bb076` |
| Non-vacuity results | RulesFloorNV-results-2026.09.15.txt · `2130c84486e96765` |
| *Superseded:* combined 0024/0025 draft | topak-adr-0024-0025-promotion-and-trust-anchor-2026.09.15.md · excluded |

## 4. Genesis debt ledger

| Measure | Value |
|---|---|
| Confirmation-required, ratified | 2 (0006, 0009) |
| Confirmation-required on ratification of the ready set | +3 (0028, 0015, 0022 §6) |
| Confirmation-required when written | 3 (0013, 0008 supersession, 0017 supersession) |
| Records not on disk | 20. **Recover them into files before bootstrap**; the genesis bundle cannot digest session history. |
| Bootstrap specification | Not drafted |
| Forcing function | None, by decision |
