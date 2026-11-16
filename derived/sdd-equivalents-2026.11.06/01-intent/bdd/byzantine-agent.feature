# Layer: intent · TOPAK source: Theory of Operation §1 "The premise", ADR-0007, ADR-0025 ("intent is the sole axiom")
# Gherkin has no construct for a principle. The nearest fit: the Feature narrative carries the
# principle as prose Cucumber never executes, and the scenarios are the threat model's cases,
# each phrased as what the mechanism does when the agent misbehaves. Tags make the layer findable.
@layer:intent @threat-model
Feature: An agent is Byzantine at every deployment position

  Safety never depends on what a model means or intends. Models stay out of the
  trusted computing base, and every guarantee is stated against an agent that may
  do anything its alphabet allows (ADR-0007). The Byzantine threat lives in Build,
  not Run, because Build principals author the specifications, policy and floor
  that Run is later judged against.

  Background:
    Given a Persona that may emit any token sequence
    And the mechanism admits an action only by syntactic lift from a constrained call interface

  Rule: Semantic judgment is never a lift (ADR-0007)

    Scenario: A classifier's verdict cannot add authority
      Given an Observer finding that classifies the action as "safe"
      And the action is outside the lease's alphabet
      When the action reaches the admit path
      Then the action is refused
      And the finding is recorded and not consulted

    Scenario: A classifier's verdict can subtract authority
      Given an Observer finding that classifies the action as "unsafe"
      And the action is inside the lease's alphabet
      When the action reaches the admit path
      Then the bundle tier may refuse it
      And nothing in the finding can widen what the floor permits

  Rule: The threat lives in Build

    Scenario: A Build principal authors a vacuously true gate predicate
      Given a proposed floor entry that no well-typed request can satisfy
      When the floor gates run before promotion
      Then the non-vacuity gate fails
      And the floor is not promoted

    Scenario: Silent abstention is not a pass
      Given a gate runner that emits no verdict
      When the promotion tally reads the gate evidence
      Then the artifact is not promoted
