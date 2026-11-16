"""Layer: assurance · the two Lease rows of spec/theorem-premise-binding.md as marked tests."""
import pytest

from topak.state import State, Rejected, Renewed


@pytest.mark.theorem("LeaseAuthorityMonotone")
@pytest.mark.premise("BASE")
@pytest.mark.premise("invariant(Lease_A1)")      # T-0045-31, or T-0045-37 and enc-faithful(Lease_A1)
@pytest.mark.premise("T-0045-10")                # rules issued, seats declared
@pytest.mark.grade("tested")                     # this test is the reference's edge; the code's is trusted
def test_lease_authority_monotone(live_state):
    assert live_state.apply(10, renew("a1", 1, {"Read", "Emit", "Draft"})) == Rejected("renewal widens the alphabet")
    assert live_state.apply(11, renew("a1", 1, {"Read"})) == Renewed(fence=11)


@pytest.mark.theorem("NoActionUnderFencedEpoch")
@pytest.mark.premise("BASE")
@pytest.mark.premise("invariant(Lease_A1)")
@pytest.mark.grade("tested")
def test_no_action_under_fenced_epoch(live_state):
    live_state.apply(3, {"op": "epoch_increment"})
    assert isinstance(live_state.check_live("a1", lease=1, epoch=0), Rejected)
    assert live_state.floor_calls == 0


@pytest.mark.theorem("ContainedMeansConfined")
@pytest.mark.premise("BASE")
@pytest.mark.premise("T-0045-20")               # the promoted image and profile
@pytest.mark.premise("T-0045-16")               # a rung-3 measurement: SIMULATED at the reference, so this is void
@pytest.mark.grade("tested")
def test_contained_means_confined(live_state):
    ...   # reported `void` under the reference's declaration (10-deployment/tdd/declaration.yaml)


def renew(seat, fence, alphabet, rung=0, ttl=1000):
    return {"op": "renew", "seat": seat, "fence": fence, "alphabet": alphabet, "rung": rung, "ttl_ms": ttl}
