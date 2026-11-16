package topak.fleet_test

import data.topak.bundle

base_facts := {
	"vehicle": "v1",
	"position": {"e": 41000, "n": 19000, "alt_agl_m": 2000},
	"position_tick": 1000,
	"nav_integrity": "ok",
	"fuel_pct": 62,
}

act(tool, args, facts) := {
	"action": "Actuate",
	"principal": {"seat": "t1", "domain": "run", "kind": "thinker"},
	"resource": {"tool": tool, "digest": "d"},
	"inputs": args,
	"facts": facts,
	"context": {"plane": "ap1", "planeKind": "autonomous", "tick": 1000},
}

orbit := {"e": 41000, "n": 19000, "alt_agl_m": 2000, "radius_m": 800}

transit := {"e": 30000, "n": 19000, "alt_agl_m": 2000, "speed_mps": 28}

test_orbit_passes if {
	bundle.allow with input as act("flight.orbit", orbit, base_facts)
}

test_transit_passes if {
	bundle.allow with input as act("flight.transit", transit, base_facts)
}

test_comms_needs_no_fix if {
	bundle.allow with input as act("comms.downlink", {"product": {"handle": {"id": 1}}}, {"vehicle": "v1"})
}

test_route_refused_at_autonomous_plane if {
	not bundle.allow with input as {"action": "Route", "principal": {"kind": "orchestrator"}, "resource": {"edge": "x"}, "context": {"plane": "ap1", "planeKind": "autonomous"}}
}

test_build_action_refused_at_autonomous_plane if {
	not bundle.allow with input as {"action": "Submit", "principal": {"kind": "thinker"}, "context": {"plane": "ap1", "planeKind": "autonomous"}}
}

test_observer_cannot_actuate if {
	inp := object.union(act("flight.orbit", orbit, base_facts), {"principal": {"kind": "observer"}})
	not bundle.allow with input as inp
}

test_no_fix_refused if {
	not bundle.allow with input as act("flight.orbit", orbit, {"vehicle": "v1", "nav_integrity": "ok", "fuel_pct": 62})
}

test_stale_fix_refused if {
	not bundle.allow with input as act("flight.orbit", orbit, object.union(base_facts, {"position_tick": 998}))
}

test_one_tick_old_fix_passes if {
	bundle.allow with input as act("flight.orbit", orbit, object.union(base_facts, {"position_tick": 999}))
}

test_degraded_nav_refused if {
	not bundle.allow with input as act("sensor.eoir_collect", {"e": 41000, "n": 19000, "mode": "wide"}, object.union(base_facts, {"nav_integrity": "degraded"}))
}

test_altitude_limit if {
	not bundle.allow with input as act("flight.orbit", object.union(orbit, {"alt_agl_m": 4501}), base_facts)
}

test_too_slow_refused if {
	not bundle.allow with input as act("flight.transit", object.union(transit, {"speed_mps": 17}), base_facts)
}

test_too_fast_refused if {
	not bundle.allow with input as act("flight.transit", object.union(transit, {"speed_mps": 36}), base_facts)
}

test_tight_orbit_refused if {
	not bundle.allow with input as act("flight.orbit", object.union(orbit, {"radius_m": 299}), base_facts)
}

test_below_bingo_no_station_work if {
	not bundle.allow with input as act("flight.orbit", orbit, object.union(base_facts, {"fuel_pct": 24}))
}

test_below_bingo_transit_still_passes if {
	bundle.allow with input as act("flight.transit", transit, object.union(base_facts, {"fuel_pct": 24}))
}

# Scoped to the autonomous plane: on a commanded plane this bundle is not on the chain at all, and
# must not be read as refusing what it never sees.
test_inert_off_the_autonomous_plane if {
	bundle.allow with input as {"action": "Route", "principal": {"kind": "orchestrator"}, "resource": {"edge": "e-go"}, "context": {"plane": "ib1", "planeKind": "commanded"}}
}
