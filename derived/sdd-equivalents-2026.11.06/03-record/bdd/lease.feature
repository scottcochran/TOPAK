# Layer: record · BDD (Cucumber / SpecFlow / Behave) · TOPAK source: ADR-0031 §4, §5, as the clause file beside this one states them
# This is the paper's "spec-anchored" form: scenarios are the record and the test. One Rule per
# guarantee; scenarios are the mutation tests of spec/Lease_A1.tla restated as behaviour.
@layer:record @ADR-0031
Feature: The lease is the composite credential

  Background:
    Given the genesis rules are issued and seat "a1" is declared
    And a grant for seat "a1" at log index 1 with alphabet Read, Emit, rung 0 and ttl 1000 ms

  @s4.1
  Rule: A renewal never adds authority

    Scenario Outline: A widening renewal is refused and the live lease is unchanged
      When seat "a1" renews with alphabet <alphabet>, rung <rung> and ttl <ttl> ms
      Then the renewal is rejected with "<reason>"
      And seat "a1" still holds the lease at fence 1

      Examples: Lease_A1.tla M_RENEW
        | alphabet          | rung | ttl  | reason                        |
        | Read, Emit, Draft | 0    | 1000 | renewal widens the alphabet   |
        | Read              | 1    | 1000 | renewal changes confinement rung |
        | Read              | 0    | 2000 | renewal lengthens the TTL     |

    Scenario: A narrowing renewal is applied at a new fence
      When seat "a1" renews with alphabet Read, rung 0 and ttl 500 ms at log index 20
      Then the renewal is applied and seat "a1" holds the lease at fence 20
      And an action under the lease at fence 1 is refused
      And an action under the lease at fence 20 is admitted

  @s4.2
  Rule: A renewal keeps round, role, bundle and confinement; changing any is a grant

    Scenario Outline: A renewal that changes a fixed field is refused
      When seat "a1" renews with <field> changed
      Then the renewal is rejected with "renewal changes <field>"

      Examples: Lease_A1.tla M_ROLE, M_LOWER; ADR-0031 R1, R2, A1
        | field              |
        | role               |
        | round              |
        | bundle             |
        | confinement digest |

  @s4.4
  Rule: A renewal's TTL is at most T_persona

    Scenario: An over-long renewal is refused by the mechanism, not by policy
      Given T_persona is 3600000 ms
      When seat "a1" renews with ttl 3600001 ms
      Then the renewal is rejected with "renewal ttl 3600001 ms exceeds T_persona 3600000 ms"

  @s5.2 @s5.3
  Rule: The epoch fence stops the fleet, ahead of the floor

    Scenario: No action under a fenced epoch
      Given a grant for seat "a2" at log index 2 with alphabet Read
      When the epoch is incremented at log index 3
      Then seats "a1" and "a2" hold no live lease
      And a Read by seat "a1" under the lease at fence 1 is refused with "FencedEpoch"
      And the floor was not consulted

  @s5.1 @s5.5
  Rule: A targeted revocation stops one principal and bars its later grants

    Scenario: Only the named principal stops
      Given a grant for seat "a2" at log index 2 with alphabet Read
      When principal "a1" is revoked at log index 3
      Then seat "a1" holds no live lease
      And seat "a2" holds the lease at fence 2
      And a later grant for seat "a1" is rejected
