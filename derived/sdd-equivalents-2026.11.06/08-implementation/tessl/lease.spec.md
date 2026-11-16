<!-- Layer: implementation · Tessl: the spec is the source; `tessl build` regenerates ./generated and runs the linked tests · TOPAK source: lease.rs::check_renewal -->
<!-- This is the same spec as 03-record/tessl/lease.spec.md; at the implementation layer the artifact that matters is the generated module beside it, which is never hand-edited. The edge is *generated* in form (the generator is an LLM, not a pinned deterministic tool), so by ADR-0057 §3 what it leaves to a person is the generator plus the reader of the tests: in practice *tested*, by the linked tests, and no stronger. -->

# Lease

See `../../03-record/tessl/lease.spec.md` for the capabilities. This copy pins the generation target.

## API

```ts
export function checkRenewal(live: Lease, next: Lease): { ok: true } | { ok: false; reason: string };
```

## Generation

- Target: `./generated/lease.ts` [@generate]
- Tests: `./tests/*.test.ts` run on every build; a failing test rejects the generated module, not the spec.
