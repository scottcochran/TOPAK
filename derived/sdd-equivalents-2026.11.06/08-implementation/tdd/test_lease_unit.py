"""Layer: implementation · TDD · the unit tests that made topak/lease.py go green (red first)."""
import pytest
from topak.lease import Confinement, Lease, RenewalRefused

L = Lease(principal="a1", seat="a1", persona="p", epoch=3, fence=1, rules_epoch=5, bundle="b",
          confinement=Confinement("c", 0), alphabet=frozenset({"Read", "Emit"}), round=7, role="author", ttl_ms=1000)


def test_narrowing_is_allowed():
    L.check_renewal(L.replace(alphabet=frozenset({"Read"}), ttl_ms=500, fence=20))


@pytest.mark.parametrize("change, reason", [
    (dict(alphabet=frozenset({"Read", "Emit", "Draft"})), "renewal widens the alphabet"),
    (dict(ttl_ms=2000), "renewal lengthens the TTL"),
    (dict(confinement=Confinement("c", 1)), "renewal changes confinement rung"),
    (dict(confinement=Confinement("d", 0)), "renewal changes confinement digest"),
    (dict(role="voter"), "renewal changes role"),
    (dict(round=8), "renewal changes round"),
    (dict(bundle="b2"), "renewal changes bundle"),
    (dict(epoch=4), "renewal changes epoch"),
])
def test_every_widening_or_fixed_field_change_is_refused(change, reason):
    with pytest.raises(RenewalRefused) as e:
        L.check_renewal(L.replace(**change))
    assert e.value.reason == reason


def test_the_reason_names_the_first_fixed_field_in_lease_rs_order():
    with pytest.raises(RenewalRefused) as e:
        L.check_renewal(L.replace(seat="a2", role="voter"))
    assert e.value.reason == "renewal changes seat"
