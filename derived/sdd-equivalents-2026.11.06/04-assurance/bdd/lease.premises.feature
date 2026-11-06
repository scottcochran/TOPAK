# Layer: assurance · BDD · TOPAK source: spec/theorem-premise-binding.md rows LeaseAuthorityMonotone, NoActionUnderFencedEpoch; ADR-0045 Annex A
# Gherkin has no slot for a premise. The nearest: tags that name the rows a scenario rests on, a
# Background that states them as givens, and a tag expression at run time that drops scenarios
# whose premise a deployment does not declare. That makes "void" a filtered-out scenario rather
# than a computed verdict, and it never reaches the code's edge (T-0045-28) at all.
@layer:assurance @theorem:LeaseAuthorityMonotone @premise:BASE @premise:T-0045-10
Feature: LeaseAuthorityMonotone rests on its premises

  Background: The trusted base (ADR-0045 Annex A), as given
    Given trusted-base row T-0045-1 "replicas apply the ordered log as crash-fault machines" is declared
    And trusted-base row T-0045-11 "the records are the records that were ratified" is declared
    And trusted-base row T-0045-28 "the running code refines the checked specification" is declared as a trust root
    And trusted-base row T-0045-29 "TLC at the constants run" or T-0045-31 "the prover" is declared
    And trusted-base row T-0045-10 "the resident genesis rules; seats declared" is declared

  @checked-in:Lease_A1.tla @proved-in:Lease_A1_proof.tla @breaks-under:M_RENEW @breaks-under:M_ROLE @breaks-under:M_LOWER
  Scenario: The invariant holds of the module
    When TLC runs Lease_A1.tla with Mut = "none"
    Then LeaseAuthorityMonotone is not violated
    And with Mut = "M_RENEW", "M_ROLE" or "M_LOWER" it is violated

  @grade:tested
  Scenario: The reference restates it as a test
    When "cargo test -p topak-core --test mutations lease_renewal_is_monotone_and_m_renew_is_refused" runs
    Then it passes
    # The edge from here to the module is *tested*; from the code to the module it is *trusted* (T-0045-28).

# Run for a deployment that has not declared T-0045-10:
#   cucumber --tags "not @premise:T-0045-10"
# which is the inventory computed by omission.
