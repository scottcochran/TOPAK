---
inclusion: fileMatch
fileMatchPattern: "**/lease*"
---
<!-- Layer: vocabulary · Amazon Kiro steering file · TOPAK source: narrative/glossary.md §4 -->
<!-- Kiro includes this whenever a file matching the pattern is open, so the agent uses the corpus's words. -->

# Glossary: the lease

Use these terms exactly. Do not invent synonyms (no "token", "session", "credential object").

- **Lease** — one composite credential, granted for one round, with a closed schema of twelve
  fields: principal, seat, persona, epoch, fence, rulesEpoch, bundle, confinement, alphabet,
  round, role, ttl. A capability that is not a field is not carried.
- **Fence** — the Paxos log index at grant. Also the lease's identity. Never a counter of its own.
- **One live lease** — a principal holds at most one live lease; a grant requires none is live.
- **Round-coterminous** — a lease lives exactly as long as its round.
- **Renewal only narrows** — a renewal may narrow the alphabet or shorten the TTL. It keeps
  bundle, round, role, confinement digest and rung. Changing any of those is a *grant*.
- **Grant** — the admit decision at a fresh fence where authority may increase. Consensus-ordered.
- **Targeted revocation** — ends every live lease matching a principal, Persona or confinement
  profile and bars later grants to it. The epoch and every other lease are untouched.
- **Epoch fence** — increments the epoch; every lease at the old epoch is fenced and every live
  round ends. Enforced by the mechanism before the floor is consulted.
- **Rung** — 0 none declared (always Mediated), 1 launcher-asserted, 2 measured boot, 3 confidential VM.
- **T_persona** — the bound on `ttl` at grant and every renewal.
