<!-- Layer: interface · Amazon Kiro `design.md` "Data Models" section · TOPAK source: ADR-0031 §1 -->
<!-- Kiro and Spec Kit both put interfaces in the design/plan as typed definitions the agent generates from. Spec Kit's /plan additionally writes `contracts/*.yaml` (OpenAPI), which is ../api. -->

## Data Models

### Lease (ADR-0031 §1) — twelve fields, closed

```typescript
type Digest = string;  // lowercase hex SHA-256
type ActionKind = 'Read' | 'Draft' | 'Invoke' | 'Emit' | 'Submit' | 'Vote' | 'Consult' | 'Actuate' | 'Report';

interface Lease {
  principal: string;
  seat: string;
  persona: Digest;               // attested at grant and renewal
  epoch: number;                 // any increment fences it
  fence: number;                 // Paxos log index at grant; the lease's identity
  rulesEpoch: number;
  bundle: Digest;                // fixed across renewal (R2)
  confinement: { digest: Digest; rung: 0 | 1 | 2 | 3 };   // fixed across renewal (A1); rung 0 is Mediated
  alphabet: ReadonlySet<ActionKind>;                       // renewal may only narrow
  round: number;                 // fixed across renewal (R1)
  role: 'author' | 'voter';      // fixed across renewal (R1)
  ttl_ms: number;                // ≤ T_persona (A2)
}

/** Only what a renewal may change. */
interface RenewRequest { seat: string; fence: number; alphabet: ReadonlySet<ActionKind>; rung: 0 | 1 | 2 | 3; ttl_ms: number; }
```

**Rules the type cannot carry** (implement as load checks, test each): the set is closed, so an
unknown key fails parsing; `fence` is assigned by the log, never by the request; `rung` on a
renewal must equal the live lease's.
