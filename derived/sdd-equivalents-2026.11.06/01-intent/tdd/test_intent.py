"""Layer: intent · TOPAK source: ToO §1, ADR-0007.

A TDD framework has no slot for a principle either; the nearest is a property-based test that
quantifies over *every* agent behaviour the alphabet admits, which is what "Byzantine at every
deployment position" asks for. Hypothesis draws the adversary. The test says nothing about what
the Persona meant, only what the mechanism did.
"""
from hypothesis import given, settings, strategies as st

from topak.lift import lift            # the syntactic lift (ADR-0018): bytes -> ActionRequest | None
from topak.state import State, params  # the replicated state and the archetype parameters

ALPHABET = {"Read", "Emit"}            # the lease under test holds two variants


@settings(max_examples=2000)
@given(st.binary(max_size=4096))      # anything a model could emit
def test_no_authority_outside_the_alphabet(persona_output: bytes):
    s = State.with_live_lease(seat="a1", alphabet=ALPHABET)
    req = lift(persona_output)
    if req is None:                    # not a well-formed call: nothing is lifted
        return
    decision = s.admit(req, params())
    assert decision.admitted is False or req.kind in ALPHABET


@given(st.text())
def test_a_finding_never_adds_authority(finding_text: str):
    """ADR-0007: a classifier's output enters only as an Observer finding, which may subtract."""
    s = State.with_live_lease(seat="a1", alphabet=ALPHABET)
    before = s.envelope("a1")
    s.record_finding(observer="o1", about="a1", text=finding_text, verdict="safe")
    after = s.envelope("a1")
    assert after <= before
