# Layer: vocabulary · TOPAK source: narrative/glossary.md §4 (Lease, One live lease, Fence, Renewal only narrows, Targeted revocation, Epoch fence)
# Gherkin has no glossary. The nearest fit is the `Rule:` keyword: one Rule per term, its text
# the definition, and one scenario that exemplifies it. Cucumber projects conventionally keep
# this as the ubiquitous-language feature, run but not asserted on much.
@layer:vocabulary
Feature: Vocabulary of the lease

  Rule: Lease: one composite credential, granted for one round, with a closed schema of twelve fields
    Scenario: A lease carries exactly twelve fields
      Given a lease granted to seat "a1" for round 7
      Then it has the fields principal, seat, persona, epoch, fence, rulesEpoch, bundle, confinement, alphabet, round, role, ttl
      And no other field

  Rule: Fence: the Paxos log index at grant; leases, admits and issuances are ordered by one log
    Scenario: The fence is the log index
      Given a grant applied at log index 41
      Then the lease's fence is 41

  Rule: One live lease: a principal holds at most one live lease, and a grant requires that none is live
    Scenario: A second grant while one is live is refused
      Given seat "a1" holds a live lease
      When a grant for seat "a1" is applied
      Then it is rejected

  Rule: Renewal only narrows: a renewal may narrow the alphabet or shorten the TTL and keeps bundle, round, role and confinement
    Scenario: A narrowing renewal
      Given seat "a1" holds a live lease with alphabet Read, Emit
      When it is renewed with alphabet Read
      Then the renewal is applied at a new fence

  Rule: Targeted revocation: ends the leases that match a principal, a Persona or a confinement profile, and bars later grants
    Scenario: Only the named principal stops
      Given seats "a1" and "a2" hold live leases
      When principal "a1" is revoked
      Then "a1" holds no live lease
      And "a2" still does

  Rule: Epoch fence: ends every live round; prior-epoch actions are rejected by the mechanism, not by policy
    Scenario: Everything stops
      Given seats "a1" and "a2" hold live leases at epoch 3
      When the epoch is fenced
      Then no seat holds a live lease
