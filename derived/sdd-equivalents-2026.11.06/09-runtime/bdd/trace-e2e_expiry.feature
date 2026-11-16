# Layer: runtime · BDD · TOPAK source: a recorded trace (topak-core trace.rs → TOPAK_TRACE_DIR/e2e_expiry_an_expired_lease_is_ended_and_refused_3.jsonl, 10 steps), replayed through spec/Mechanism.tla
# BDD's runtime artifact runs the other way from TOPAK's: a scenario is written and then executed.
# The nearest equivalent of trace replay is a feature *generated from a trace*: each recorded apply
# becomes a step, each projected state an assertion, and running it through the step definitions
# (08-implementation) re-executes the recorded behaviour against the current code. That is a
# regression replay, not a check against the model; the model does not appear.
# GENERATED from a trace by trace2feature (hypothetical) · 2026-11-06 · do not edit
@layer:runtime @generated-from-trace @suite:topak-node/e2e
Feature: Replay of trace e2e_expiry_an_expired_lease_is_ended_and_refused_3

  Scenario: The recorded 10 steps reproduce
    Given the projected initial state of the trace
    When log index 1 applies Issue (genesis rules; oracle: issuance valid)
    Then the projected state matches step 1
    When log index 2 applies Grant seat "a1", alphabet Read, Emit, rung 0, ttl 50 ms
    Then the result is LeaseGranted fence 2
    And the projected state matches step 2
    When log index 3 applies Admit seat "a1" lease 2 Read (oracle: params digest ok)
    Then the result is Admitted
    When the local clock passes 50 ms and log index 4 applies EndRound seat "a1" fence 2 reason expired
    Then the result is RoundEnded
    And seat "a1" holds no live lease
    When log index 5 applies Admit seat "a1" lease 2 Read
    Then the result is Rejected "no live lease"
    And the floor was not consulted
    And the projected state matches step 5
    # steps 6–10 elided
