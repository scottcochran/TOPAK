"""Layer: implementation · BDD (behave step definitions) · TOPAK source: topak-core lease.rs, state.rs, as 03-record/bdd/lease.feature drives them.

In BDD the implementation-layer artifact is the step definition: the glue that binds each Gherkin
line to the code. The feature file is the record; this file is the *tested* edge from the code to it
(ADR-0057 §3). Nothing here states a property; it only says which code each sentence calls.
"""
from behave import given, when, then
from topak.state import State, Rejected, Renewed, LeaseGranted, FencedEpoch


@given("the genesis rules are issued and seat \"{seat}\" is declared")
def step_genesis(ctx, seat):
    ctx.state = State.genesis(seats=[seat, "a2"])
    ctx.result = None


@given("a grant for seat \"{seat}\" at log index {index:d} with alphabet {alphabet}, rung {rung:d} and ttl {ttl:d} ms")
@given("a grant for seat \"{seat}\" at log index {index:d} with alphabet {alphabet}")
def step_grant(ctx, seat, index, alphabet, rung=0, ttl=1000):
    r = ctx.state.apply(index, {"op": "grant", "seat": seat, "alphabet": _alph(alphabet), "rung": rung, "ttl_ms": ttl})
    assert r == LeaseGranted(fence=index), r


@when("seat \"{seat}\" renews with alphabet {alphabet}, rung {rung:d} and ttl {ttl:d} ms")
@when("seat \"{seat}\" renews with alphabet {alphabet}, rung {rung:d} and ttl {ttl:d} ms at log index {index:d}")
def step_renew(ctx, seat, alphabet, rung, ttl, index=10):
    ctx.result = ctx.state.apply(index, {"op": "renew", "seat": seat, "fence": ctx.state.live_by_seat[seat],
                                         "alphabet": _alph(alphabet), "rung": rung, "ttl_ms": ttl})


@when("seat \"{seat}\" renews with {field} changed")
def step_renew_changed(ctx, seat, field):
    ctx.result = ctx.state.apply(10, {"op": "renew", "seat": seat, "fence": ctx.state.live_by_seat[seat],
                                      "alphabet": {"Read"}, "rung": 0, "ttl_ms": 1000, field: "other"})


@when("seat \"{seat}\" renews with ttl {ttl:d} ms")
def step_renew_ttl(ctx, seat, ttl):
    step_renew(ctx, seat, "Read", 0, ttl)


@given("T_persona is {ms:d} ms")
def step_t_persona(ctx, ms):
    ctx.state.t_persona_ms = ms


@when("the epoch is incremented at log index {index:d}")
def step_fence(ctx, index):
    ctx.state.apply(index, {"op": "epoch_increment"})


@when("principal \"{p}\" is revoked at log index {index:d}")
def step_revoke(ctx, p, index):
    ctx.state.apply(index, {"op": "revoke", "target": {"kind": "principal", "id": p}})


@then("the renewal is rejected with \"{reason}\"")
def step_rejected(ctx, reason):
    assert isinstance(ctx.result, Rejected) and ctx.result.reason.startswith(reason), ctx.result


@then("the renewal is applied and seat \"{seat}\" holds the lease at fence {fence:d}")
def step_renewed(ctx, seat, fence):
    assert ctx.result == Renewed(fence=fence) and ctx.state.live_by_seat[seat] == fence


@then("seat \"{seat}\" still holds the lease at fence {fence:d}")
@then("seat \"{seat}\" holds the lease at fence {fence:d}")
def step_holds(ctx, seat, fence):
    assert ctx.state.live_by_seat[seat] == fence


@then("seat \"{seat}\" holds no live lease")
def step_no_lease(ctx, seat):
    assert seat not in ctx.state.live_by_seat


@then("seats \"{a}\" and \"{b}\" hold no live lease")
def step_none(ctx, a, b):
    assert a not in ctx.state.live_by_seat and b not in ctx.state.live_by_seat


@then("an action under the lease at fence {fence:d} is refused")
def step_refused(ctx, fence):
    assert isinstance(ctx.state.check_live("a1", lease=fence), Rejected)


@then("an action under the lease at fence {fence:d} is admitted")
def step_admitted(ctx, fence):
    assert not isinstance(ctx.state.check_live("a1", lease=fence), Rejected)


@then("a Read by seat \"{seat}\" under the lease at fence {fence:d} is refused with \"FencedEpoch\"")
def step_fenced(ctx, seat, fence):
    assert isinstance(ctx.state.check_live(seat, lease=fence, epoch=0), FencedEpoch)


@then("the floor was not consulted")
def step_no_floor(ctx):
    assert ctx.state.floor_calls == 0


@then("a later grant for seat \"{seat}\" is rejected")
def step_regrant_rejected(ctx, seat):
    assert isinstance(ctx.state.apply(99, {"op": "grant", "seat": seat, "alphabet": {"Read"}, "rung": 0, "ttl_ms": 1000}), Rejected)


def _alph(s):
    return {a.strip() for a in s.split(",")}
