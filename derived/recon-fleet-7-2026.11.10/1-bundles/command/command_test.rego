package topak.command_test

import data.topak.bundle

ctx := {"plane": "ib1", "planeKind": "commanded", "childrenSeated": 0}

person := {"seat": "orc-co", "domain": "run", "kind": "orchestrator", "actor": "person"}

route(p, edge) := {"action": "Route", "principal": p, "resource": {"edge": edge}, "context": ctx}

intent(req, seat) := {
	"action": "Intent",
	"principal": {"seat": seat, "kind": "operator", "actor": "person"},
	"request": req,
	"context": ctx,
}

seat_req(req) := {"action": "Seat", "principal": {"seat": "g1", "kind": "grant"}, "request": req, "context": ctx}

first := {"plane": "ap1", "round": 1, "expiry": {"from_tick": 0, "ticks": 2879}, "budget": 112}

test_commander_routes if {
	bundle.allow with input as route(person, "e-go")
}

test_agent_cannot_route if {
	not bundle.allow with input as route(object.union(person, {"actor": "agent"}), "e-go")
}

test_other_person_cannot_route if {
	not bundle.allow with input as route(object.union(person, {"seat": "op1"}), "e-scrub")
}

test_route_off_the_dag_refused if {
	not bundle.allow with input as route(person, "e-launch-anyway")
}

test_first_intent_allowed if {
	bundle.allow with input as intent(first, "op1")
}

test_later_intent_may_start_late if {
	bundle.allow with input as intent(object.union(first, {"round": 2, "expiry": {"from_tick": 1200, "ticks": 1679}}), "op2")
}

test_later_intent_may_not_end_late if {
	not bundle.allow with input as intent(object.union(first, {"round": 2, "expiry": {"from_tick": 1200, "ticks": 1680}}), "op2")
}

test_intent_past_24_hours_refused if {
	not bundle.allow with input as intent(object.union(first, {"expiry": {"from_tick": 0, "ticks": 2880}}), "op1")
}

test_intent_over_budget_refused if {
	not bundle.allow with input as intent(object.union(first, {"budget": 113}), "op1")
}

test_intent_from_non_operator_refused if {
	not bundle.allow with input as intent(first, "g1")
}

test_intent_elsewhere_than_ib_refused if {
	inp := object.union(intent(first, "op1"), {"context": {"plane": "ap1", "planeKind": "autonomous"}})
	not bundle.allow with input as inp
}

test_intent_with_release_refused if {
	not bundle.allow with input as intent(object.union(first, {"release": true}), "op1")
}

test_seat_fleet_plane_allowed if {
	bundle.allow with input as seat_req({"plane": "ap1", "kind": "autonomous", "release": false})
}

test_second_fleet_refused if {
	inp := object.union(seat_req({"plane": "ap1", "kind": "autonomous", "release": false}), {"context": {"childrenSeated": 1}})
	not bundle.allow with input as inp
}

test_sibling_plane_refused if {
	not bundle.allow with input as seat_req({"plane": "ap2", "kind": "autonomous", "release": false})
}

test_commanded_child_refused if {
	not bundle.allow with input as seat_req({"plane": "ap1", "kind": "commanded", "release": false})
}

test_release_child_refused if {
	not bundle.allow with input as seat_req({"plane": "ap1", "kind": "autonomous", "release": true})
}

# The command bundle is on ap1's chain and must say nothing about the vehicles' entries.
test_vehicle_entry_not_this_bundles_to_refuse if {
	bundle.allow with input as {
		"action": "Actuate",
		"principal": {"seat": "t1", "kind": "thinker"},
		"resource": {"tool": "flight.orbit", "digest": "unknown-to-this-bundle"},
		"inputs": {},
		"context": {"plane": "ap1", "planeKind": "autonomous"},
	}
}

test_unlisted_tool_at_ib_refused if {
	not bundle.allow with input as {
		"action": "Actuate",
		"principal": {"seat": "ts1", "kind": "thinker"},
		"resource": {"tool": "staff.not_listed", "digest": "x"},
		"inputs": {},
		"context": ctx,
	}
}
