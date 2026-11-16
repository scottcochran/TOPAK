<!-- Layer: policy · Stateflow Truth Table (text rendering) and its Lustre twin · TOPAK source: floor/genesis-floor.cedar B4 -->
<!-- Model-based design states a policy as a truth table or a boolean block diagram; Simulink Design Verifier can then prove the same three gates the floor runs (never errors, satisfiable, each row matters) as proof objectives, and Embedded Coder generates the C. This is as close as the paper's categories get to a verified floor evaluator, with one difference: there is no mechanized semantics of Stateflow to prove the evaluator against (T-0045-3 has one for Cedar). -->

Stateflow truth table `Floor/B4_emit_own_topic`

| # | Condition | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `action == Emit` | T | T | T | T | T | T | T | F |
| 2 | `principal.domain == build` | T | T | T | T | T | T | F | - |
| 3 | `lease.alphabet(Emit)` | T | T | T | T | T | F | - | - |
| 4 | `topic.owner == principal` | T | T | T | T | F | - | - | - |
| 5 | `topic.epoch == ctx.epoch` | T | T | T | F | - | - | - | - |
| 6 | `topic.round == ctx.round` | T | T | F | - | - | - | - | - |
| 7 | `!topic.sealed` | T | F | - | - | - | - | - | - |
| | **Action** | A1 | A2 | A2 | A2 | A2 | A2 | A2 | A2 |

Actions: `A1: permit = true; reason = "B4-emit-own-topic"` · `A2: permit = false`.

Design Verifier objectives attached to the table: every decision column is reachable (the
non-vacuity gate; a dead column is a Design Verifier "unreachable objective"), the table is
complete (the default column makes it total, which is the totality gate for a table that cannot
error), and removing column D1 changes some decision (every-entry-matters). Design Verifier
reports each as Satisfied, Unsatisfiable or Undecided.

The same entry in Lustre, for SCADE or Kind 2:

```lustre
node b4_emit_own_topic(is_emit, domain_build, alphabet_emit, owner_is_principal,
                       epoch_current, round_current, sealed: bool)
     returns (permit: bool)
(*@contract
   guarantee "non-vacuity: refutable" not (is_emit and domain_build and alphabet_emit and
             owner_is_principal and epoch_current and round_current and not sealed) => not permit;
   guarantee "sealed never permitted" sealed => not permit;
   guarantee "other owner never permitted" not owner_is_principal => not permit;
*)
let
  permit = is_emit and domain_build and alphabet_emit and owner_is_principal
           and epoch_current and round_current and not sealed;
tel
```
