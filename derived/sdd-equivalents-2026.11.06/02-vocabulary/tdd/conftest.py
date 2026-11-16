"""Layer: vocabulary · TOPAK source: narrative/glossary.md §4.

pytest's vocabulary is its fixtures. A fixture per term, its docstring the definition, gives
every test the same words for the same things, which is what a glossary is for. `pytest
--fixtures` prints the glossary.
"""
import pytest

from topak.lease import Lease, Confinement
from topak.state import State


@pytest.fixture
def lease() -> Lease:
    """Lease: one composite credential, granted for one round, with a closed schema of twelve
    fields: principal, seat, persona, epoch, fence, rulesEpoch, bundle, confinement, alphabet,
    round, role and ttl (ADR-0031 §1). A capability that is not a field is not carried."""
    return Lease(principal="a1", seat="a1", persona="p-1", epoch=3, fence=41, rules_epoch=5,
                 bundle="b-1", confinement=Confinement(digest="c-0", rung=0),
                 alphabet=frozenset({"Read", "Emit"}), round=7, role="author", ttl_ms=1000)


@pytest.fixture
def fence(lease) -> int:
    """Fence: the Paxos log index at grant. Leases, admits and issuances are ordered by one log
    (ADR-0031 §2)."""
    return lease.fence


@pytest.fixture
def live_state(lease) -> State:
    """One live lease: a principal holds at most one live lease, and a grant requires that none
    is live (ADR-0031 §2). This state holds exactly one, the `lease` fixture's."""
    s = State.genesis()
    s.apply_grant(lease)
    return s


@pytest.fixture
def narrowing(lease) -> Lease:
    """Renewal only narrows: a renewal may narrow the alphabet or shorten the TTL. It keeps the
    bundle, the round, the role and the confinement digest and rung (ADR-0031 §4, A1)."""
    return lease.replace(alphabet=frozenset({"Read"}), ttl_ms=500)


@pytest.fixture
def epoch_fence(live_state):
    """Epoch fence: ends every live round. After an epoch increment, prior-epoch actions are
    rejected by the mechanism, not by policy (ADR-0031 §5, ADR-0022 §2)."""
    def fence():
        live_state.apply_epoch_increment()
        return live_state.epoch
    return fence
