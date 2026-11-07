<!-- Layer: intent · Simulink Requirements (slreq) requirement set, shown as the Requirements Editor table · TOPAK source: ToO §1, ADR-0007 -->
<!-- Model-based design keeps intent as *Informational* requirements at the root of the set, linked downward by `Implements`/`Verifies`. SCADE has no slot for intent; its requirements come from an external tool (DOORS, Polarion). -->

Requirement set: `topak_intent.slreqx`

| ID | Summary | Description | Rationale | Type |
|---|---|---|---|---|
| INT-1 | Byzantine agent | An agent is Byzantine at every deployment position. No guarantee rests on what a model means or intends. | Models cannot be specified; keeping them outside the verified object is what makes the object verifiable. | Informational |
| INT-1.1 | Syntactic lift only | A field enters the admit path only by mechanical, total extraction from a constrained call interface. | A semantic lift reintroduces the model into the trusted base. | Functional |
| INT-1.2 | Findings subtract | A classifier's verdict enters only as an Observer finding and may subtract authority, never add it. | Keeps judgment advisory and the mechanism authoritative. | Functional |
| INT-2 | The threat is in Build | Build principals author the specifications, policy and floor Run is judged against; every gate assumes an adversarial author. | Moon & Varshney's empirical failure is a Build failure. | Informational |
| INT-2.1 | Non-vacuity | Every floor entry has a request that satisfies it and one that does not. | A vacuously true predicate is the Build failure mode. | Functional |
| INT-3 | Monotone subtraction | Renewal narrows; bundles subtract; revocation needs no quorum; adding authority is consensus-ordered. | Puts every authority increase on the ordered path. | Functional |

Link types used from this set: `INT-1.1 ←Implements— Mechanism/Lift`, `INT-2.1 ←Verifies— FloorGates/NonVacuity`, `INT-3 ←Implements— Lease/Renew`.
