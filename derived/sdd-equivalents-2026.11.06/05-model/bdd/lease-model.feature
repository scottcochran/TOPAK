# Layer: model · BDD · TOPAK source: spec/Lease_A1.tla, its mutations and reachability witnesses (G2 §3 convention)
# Gherkin cannot state an invariant over all behaviours. What it can carry is the module's
# *evidence structure*: each mutation as a scenario that must fail a property, each witness as a
# scenario that must be reachable. This is the results file (Lease_A1-results-2026.09.28.txt) as
# behaviour, not the module. TLC still has to exist to run it.
@layer:model @module:Lease_A1
Feature: Lease_A1.tla, its mutations and its witnesses

  Background:
    Given Lease_A1.tla with Principals {p1, p2}, Acts {Read, Emit}, Rungs 0..3, MaxEpoch 2 and MaxFence 4

  Rule: Every property holds of the unmutated module

    Scenario Outline: <property> is an invariant under Mut = "none"
      When TLC checks <property> with Mut = "none"
      Then no error is found
      Examples:
        | property                  |
        | LeaseAuthorityMonotone    |
        | NoActionUnderFencedEpoch  |
        | Rung0NeverContained       |
        | RevokedStaysStopped       |

  Rule: Every mutation is caught by the property it breaks (ADR-0046: a module tells the clause from its negation)

    Scenario Outline: <mutation> violates <property>
      When TLC checks <property> with Mut = "<mutation>"
      Then the invariant is violated
      Examples: the "Breaks under" column of theorem-premise-binding.md
        | mutation  | property                  | what the mutation does                                   |
        | M_RENEW   | LeaseAuthorityMonotone    | renewal may issue any authority                          |
        | M_ROLE    | LeaseAuthorityMonotone    | renewal checks alphabet and rung but not the role        |
        | M_LOWER   | LeaseAuthorityMonotone    | renewal may lower the rung (the frozen §4 rule)          |
        | M_FENCE   | NoActionUnderFencedEpoch  | an action is admitted under a stale lease epoch          |
        | M_RUNG    | Rung0NeverContained       | Contained ignores the rung                               |
        | M_REVOKE  | RevokedStaysStopped       | a grant ignores the revocation set                       |

  Rule: Every witness is reachable (non-vacuity: the properties are not true for want of behaviour)

    Scenario Outline: <witness> is violated
      When TLC checks <witness> with Mut = "none"
      Then the invariant is violated, which is the expected result
      Examples:
        | witness               | the behaviour it proves exists                                   |
        | NeverActed            | some action is admitted                                          |
        | NeverRenewed          | some lease is renewed                                            |
        | NeverRenewedAbove0    | some lease above rung 0 is renewed (A1)                          |
        | NeverRevoked          | the epoch is incremented                                         |
        | NeverStaleLease       | a lease outlives a fence                                         |
        | NeverSelectiveRevoke  | one principal is revoked while another's lease stays live        |
