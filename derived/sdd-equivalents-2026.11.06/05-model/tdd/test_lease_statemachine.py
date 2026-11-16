"""Layer: model · TDD · TOPAK source: spec/Lease_A1.tla.

A TDD framework's counterpart of a TLA+ module is a stateful property test: Hypothesis's
RuleBasedStateMachine explores sequences of Grant/Renew/Act/Revoke/RevokeLease/EndRound and
checks the four invariants after every step. It is the module's state machine, its mutations as a
parameter, and its invariants, in the language the code is tested in. Where TLC enumerates every
state at the constants, Hypothesis samples; where TLAPS proves for every constant, this proves nothing.
Run: pytest test_lease_statemachine.py --hypothesis-seed=0 -k 'none'
"""
import pytest
from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

PRINCIPALS = ["p1", "p2"]
ACTS = frozenset({"Read", "Emit"})
RUNGS = range(0, 4)
ROLES = ["author", "voter"]
MAX_EPOCH, MAX_FENCE = 2, 6
NO_LEASE = dict(live=False, alphabet=frozenset(), rung=0, role="none", epoch=0, fence=0)


class LeaseModel(RuleBasedStateMachine):
    Mut = "none"      # subclassed per mutation below

    def __init__(self):
        super().__init__()
        self.lease = {p: dict(NO_LEASE) for p in PRINCIPALS}
        self.prev = {p: dict(NO_LEASE) for p in PRINCIPALS}
        self.epoch = self.fence = 0
        self.acted = set()
        self.stale_admitted = False
        self.revoked = set()

    # --- the actions of Lease_A1.tla ------------------------------------------------------------
    def narrows(self, new, old):       return new["alphabet"] <= old["alphabet"]
    def refines(self, new, old):       return self.narrows(new, old) and new["rung"] == old["rung"] and new["role"] == old["role"]

    def renewal_allowed(self, new, old):
        if self.Mut == "M_RENEW": return True
        if self.Mut == "M_ROLE":  return self.narrows(new, old) and new["rung"] == old["rung"]
        if self.Mut == "M_LOWER": return self.narrows(new, old) and new["rung"] <= old["rung"] and new["role"] == old["role"]
        return self.refines(new, old)

    @precondition(lambda self: self.fence < MAX_FENCE)
    @rule(p=st.sampled_from(PRINCIPALS), a=st.frozensets(st.sampled_from(sorted(ACTS))), r=st.sampled_from(RUNGS), ro=st.sampled_from(ROLES))
    def grant(self, p, a, r, ro):
        if self.lease[p]["live"]: return
        if self.Mut != "M_REVOKE" and p in self.revoked: return
        self.prev[p] = self.lease[p]
        self.fence += 1
        self.lease[p] = dict(live=True, alphabet=a, rung=r, role=ro, epoch=self.epoch, fence=self.fence)

    @precondition(lambda self: self.fence < MAX_FENCE)
    @rule(p=st.sampled_from(PRINCIPALS), a=st.frozensets(st.sampled_from(sorted(ACTS))), r=st.sampled_from(RUNGS), ro=st.sampled_from(ROLES))
    def renew(self, p, a, r, ro):
        old = self.lease[p]
        if not old["live"] or old["epoch"] != self.epoch: return
        new = dict(live=True, alphabet=a, rung=r, role=ro, epoch=self.epoch, fence=self.fence + 1)
        if not self.renewal_allowed(new, old): return
        self.prev[p], self.lease[p], self.fence = old, new, self.fence + 1

    @precondition(lambda self: self.epoch < MAX_EPOCH)
    @rule()
    def revoke(self):                       # the fleet fence
        self.epoch += 1

    @rule(p=st.sampled_from(PRINCIPALS), a=st.sampled_from(sorted(ACTS)))
    def act(self, p, a):
        l = self.lease[p]
        epoch_ok = True if self.Mut == "M_FENCE" else l["epoch"] == self.epoch
        if not (l["live"] and epoch_ok and a in l["alphabet"]): return
        self.acted.add((p, a, self.epoch, l["epoch"]))
        self.stale_admitted |= l["epoch"] != self.epoch

    @rule(p=st.sampled_from(PRINCIPALS))
    def revoke_lease(self, p):              # R3: targeted
        if p in self.revoked: return
        self.revoked.add(p)
        self.lease[p] = self.prev[p] = dict(NO_LEASE)

    @rule(p=st.sampled_from(PRINCIPALS))
    def end_round(self, p):
        if not self.lease[p]["live"]: return
        self.lease[p] = self.prev[p] = dict(NO_LEASE)

    def contained(self, p):
        l = self.lease[p]
        return l["live"] and (True if self.Mut == "M_RUNG" else l["rung"] >= 1)

    # --- the properties -------------------------------------------------------------------------
    @invariant()
    def lease_authority_monotone(self):
        for p in PRINCIPALS:
            l, q = self.lease[p], self.prev[p]
            if l["live"] and q["live"] and l["epoch"] == q["epoch"]:
                assert self.refines(l, q), f"LeaseAuthorityMonotone violated for {p}"

    @invariant()
    def no_action_under_fenced_epoch(self):
        assert not self.stale_admitted
        assert all(le == at for (_, _, at, le) in self.acted)

    @invariant()
    def rung0_never_contained(self):
        for p in PRINCIPALS:
            if self.lease[p]["live"] and self.lease[p]["rung"] == 0:
                assert not self.contained(p)

    @invariant()
    def revoked_stays_stopped(self):
        assert all(not self.lease[p]["live"] for p in self.revoked)


# The unmutated module must pass; each mutation must fail (the results file, as test outcomes).
TestLease_none = LeaseModel.TestCase
TestLease_none.settings = settings(max_examples=500, stateful_step_count=30)

for mut in ["M_RENEW", "M_FENCE", "M_RUNG", "M_ROLE", "M_REVOKE", "M_LOWER"]:
    cls = type(f"Lease_{mut}", (LeaseModel,), {"Mut": mut})
    globals()[f"test_{mut}_is_caught"] = pytest.mark.xfail(strict=True, reason=f"{mut} must violate a property")(cls.TestCase)
