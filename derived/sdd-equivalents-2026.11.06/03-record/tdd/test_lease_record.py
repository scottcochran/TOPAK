"""Layer: record · TDD (pytest) · TOPAK source: ADR-0031 §4, §5.

The paper's TDD form: a test per guarantee, written first, against an interface that does not
exist yet (`topak.lease`, `topak.state`). Each test's name is the guarantee's number so a
failure names the clause. The Hypothesis test at the end is the one that says *never*.
"""
import pytest
from hypothesis import given, strategies as st

from topak.lease import Lease, Confinement
from topak.state import State, Rejected, Renewed, LeaseGranted, FencedEpoch

ALPH = ["Read", "Draft", "Invoke", "Emit", "Submit"]


@pytest.fixture
def s():
    s = State.genesis()
    assert s.apply(1, grant("a1", {"Read", "Emit"})) == LeaseGranted(fence=1)
    return s


def grant(seat, alphabet, rung=0, ttl=1000):
    return {"op": "grant", "seat": seat, "alphabet": alphabet, "rung": rung, "ttl_ms": ttl}


def renew(seat, fence, alphabet, rung=0, ttl=1000, **changed):
    return {"op": "renew", "seat": seat, "fence": fence, "alphabet": alphabet, "rung": rung, "ttl_ms": ttl, **changed}


# §4.1 ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("req, reason", [
    (renew("a1", 1, {"Read", "Emit", "Draft"}), "renewal widens the alphabet"),
    (renew("a1", 1, {"Read"}, rung=1), "renewal changes confinement rung"),
    (renew("a1", 1, {"Read"}, ttl=2000), "renewal lengthens the TTL"),
])
def test_s4_1_a_widening_renewal_is_refused(s, req, reason):
    assert s.apply(10, req) == Rejected(reason)
    assert s.live_by_seat["a1"] == 1, "a refused renewal leaves the lease as it was"


def test_s4_1_a_narrowing_renewal_moves_the_lease_to_a_new_fence(s):
    assert s.apply(20, renew("a1", 1, {"Read"}, ttl=500)) == Renewed(fence=20)
    assert s.live_by_seat["a1"] == 20
    assert isinstance(s.check_live("a1", lease=1), Rejected)
    assert s.check_live("a1", lease=20) is not None


# §4.2 ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("field", ["role", "round", "bundle", "confinement digest"])
def test_s4_2_a_renewal_that_changes_a_fixed_field_is_a_grant_not_a_renewal(s, field):
    assert s.apply(10, renew("a1", 1, {"Read"}, **{field: "other"})) == Rejected(f"renewal changes {field}")


# §4.4 ----------------------------------------------------------------------------------------
def test_s4_4_a_ttl_over_t_persona_is_refused_at_renewal(s):
    assert s.apply(10, renew("a1", 1, {"Read"}, ttl=s.t_persona_ms + 1)) == Rejected(
        f"renewal ttl {s.t_persona_ms + 1} ms exceeds T_persona {s.t_persona_ms} ms (ADR-0031 A2)")


# §5.2, §5.3 ----------------------------------------------------------------------------------
def test_s5_2_the_epoch_fence_ends_every_live_lease_ahead_of_the_floor(s):
    s.apply(2, grant("a2", {"Read"}))
    s.apply(3, {"op": "epoch_increment"})
    assert s.live_by_seat == {}
    deny = s.check_live("a1", lease=1, epoch=0)
    assert deny == FencedEpoch(lease=0, current=1)
    assert s.floor_calls == 0


# §5.1, §5.5 ----------------------------------------------------------------------------------
def test_s5_1_a_targeted_revocation_stops_one_principal_and_bars_later_grants(s):
    s.apply(2, grant("a2", {"Read"}))
    s.apply(3, {"op": "revoke", "target": {"kind": "principal", "id": "a1"}})
    assert "a1" not in s.live_by_seat and s.live_by_seat["a2"] == 2
    assert isinstance(s.apply(4, grant("a1", {"Read"})), Rejected)


# §4.1 as a property ---------------------------------------------------------------------------
@given(st.frozensets(st.sampled_from(ALPH)), st.integers(0, 3), st.integers(0, 5000))
def test_s4_1_never_adds_authority(alphabet, rung, ttl):
    s = State.genesis()
    s.apply(1, grant("a1", {"Read", "Emit"}, ttl=1000))
    r = s.apply(2, renew("a1", 1, alphabet, rung=rung, ttl=ttl))
    if r == Renewed(fence=2):
        new = s.leases[2]
        assert new.alphabet <= {"Read", "Emit"} and new.confinement.rung == 0 and new.ttl_ms <= 1000
    else:
        assert isinstance(r, Rejected)
