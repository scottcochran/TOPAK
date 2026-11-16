# Layer: interface · BDD · TOPAK source: ADR-0031 §1
# Gherkin is a poor schema language; what it can say is that the schema is closed and what each
# field is for. A data table carries the field list; the scenarios are the load checks.
@layer:interface
Feature: The lease has twelve fields and the set is closed

  Scenario: The fields
    Given a lease
    Then it has exactly these fields
      | field       | type                        | at grant | for the round |
      | principal   | string                      | checked  | assumed       |
      | seat        | string                      | checked  | assumed       |
      | persona     | digest                      | checked  | assumed       |
      | epoch       | integer                     | assigned | compared      |
      | fence       | integer (log index)         | assigned | compared      |
      | rulesEpoch  | integer                     | assigned | compared      |
      | bundle      | digest                      | checked  | assumed       |
      | confinement | {digest, rung 0..3}         | checked  | assumed       |
      | alphabet    | set of ActionKind           | checked  | assumed       |
      | round       | integer                     | checked  | assumed       |
      | role        | author or voter             | checked  | assumed       |
      | ttl_ms      | integer, at most T_persona  | assigned | assumed on a sound clock |

  Scenario: A thirteenth field is refused
    Given a lease document with an extra field "scope"
    When the mechanism parses it
    Then parsing fails
    And the failure names "scope"

  Scenario: A missing field is refused
    Given a lease document without "fence"
    When the mechanism parses it
    Then parsing fails
