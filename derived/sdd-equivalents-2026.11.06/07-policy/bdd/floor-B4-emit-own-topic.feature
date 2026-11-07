# Layer: policy · BDD · TOPAK source: floor/genesis-floor.cedar entry B4-emit-own-topic; floor/genesis-tests.json (the 62 behavioural cases)
# The floor's case file is already BDD in shape: every permit has a case that allows and one that
# denies, and every forbid is the reason for some deny. Here it is as Gherkin: a Scenario Outline per
# entry, examples from gen-tests.py. Cucumber runs them through `cedar authorize`; nothing in Gherkin
# can carry the gates (totality, non-vacuity, discrimination), which quantify over schema S.
@layer:policy @floor:B4-emit-own-topic @ADR-0022-s1
Feature: B4: a Build seat emits only to its own, unsealed topic at the current epoch and round

  Background:
    Given the genesis floor and schema S
    And epoch 3, round 7 and rules epoch 5
    And Build seat "a1" of kind thinker, holding a lease with alphabet Read, Draft, Invoke, Emit, Submit
    And the floor is evaluated as: any satisfied forbid denies; else any satisfied permit allows; else deny
    And any evaluation error is a deny

  Scenario Outline: Emit to <topic>
    Given topic "<topic>" owned by "<owner>" at epoch <epoch>, round <round>, sealed <sealed>
    When seat "a1" requests Emit on topic "<topic>"
    Then the decision is <decision>
    And the reasons are <reasons>

    Examples: from floor/gen-tests.py
      | topic         | owner | epoch | round | sealed | decision | reasons              |
      | a1-r7         | a1    | 3     | 7     | false  | Allow    | B4-emit-own-topic    |
      | v1-r7         | v1    | 3     | 7     | false  | Deny     | (no permit matched)  |
      | a1-r7-sealed  | a1    | 3     | 7     | true   | Deny     | (no permit matched)  |
      | a1-e2         | a1    | 2     | 7     | false  | Deny     | (no permit matched)  |

  Scenario: Emit without Emit in the alphabet
    Given seat "a1" holds a lease with alphabet Read, Draft
    And topic "a1-r7" owned by "a1" at epoch 3, round 7, sealed false
    When seat "a1" requests Emit on topic "a1-r7"
    Then the decision is Deny

  Scenario: Emit by a Run seat is refused by domain, not by topic
    Given Run seat "r1" of kind thinker
    And topic "r1-r7" owned by "r1" at epoch 3, round 7, sealed false
    When seat "r1" requests Emit on topic "r1-r7"
    Then the decision is Deny
    # Run's variant is Report (ADR-0040); Emit on a Run seat matches no Build envelope.
