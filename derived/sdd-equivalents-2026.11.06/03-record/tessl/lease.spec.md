<!-- Layer: record · Tessl spec (`lease.spec.md`), the "spec-as-source" tool of the paper · TOPAK source: ADR-0031 §4, §5 -->
<!-- In Tessl the spec is the maintained artifact; `tessl build` generates the module and runs the linked tests, and the code is never hand-edited. The format: a title, prose, `## Capabilities` with a test link per statement, `## API` with signatures. Approximated from Tessl's published examples; the exact grammar is theirs. -->

# Lease

The composite credential of ADR-0031. A lease is granted for one round, holds a closed set of
twelve fields, and is identified by its fence, the log index it was applied at. This module
decides renewals and applies the two tools that end a lease.

## Capabilities

### Renewal only narrows

- A renewal whose alphabet is not a subset of the live lease's is refused with
  `renewal widens the alphabet`, and the live lease is unchanged. [@test](tests/renew-widens.test.ts)
- A renewal whose ttl is longer than the live lease's is refused with
  `renewal lengthens the TTL`. [@test](tests/renew-ttl.test.ts)
- A renewal that changes round, role, bundle, confinement digest or rung is refused with
  `renewal changes <field>`. [@test](tests/renew-fixed-fields.test.ts)
- A narrowing renewal is applied at the current log index; the old lease ends with reason
  `renewed` and the new index becomes the seat's live lease. [@test](tests/renew-narrows.test.ts)
- A renewal whose ttl exceeds `T_persona` is refused. [@test](tests/renew-t-persona.test.ts)

### Targeted revocation

- Ends every live lease matching the target and bars every later grant matching it; the epoch
  and every other lease are untouched. [@test](tests/revoke.test.ts)
- Is permanent within the rules-epoch chain. [@test](tests/revoke-permanent.test.ts)

### Epoch fence

- Incrementing the epoch ends every live lease with reason `fenced`. [@test](tests/fence.test.ts)
- An action naming a lease at a non-current epoch is refused with `FencedEpoch` before any
  policy is consulted. [@test](tests/fence-ahead-of-floor.test.ts)

## API

```ts
export type Reason = string;
export function checkRenewal(live: Lease, next: Lease): { ok: true } | { ok: false; reason: Reason };
export function applyRenew(state: State, index: number, req: RenewRequest): Applied;
export function applyRevoke(state: State, index: number, target: RevocationTarget): Applied;
export function applyEpochIncrement(state: State, index: number): Applied;
export function checkLive(state: State, req: ActionRequest): LeaseRecord | MechanismDeny;
```

## Dependencies

- [@use](../06-interface/api/lease.schema.json) — the lease's twelve fields.
