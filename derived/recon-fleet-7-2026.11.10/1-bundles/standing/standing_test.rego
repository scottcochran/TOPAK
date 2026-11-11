package topak.bundle_test

import data.topak.bundle

effect := {"class": "reversible", "t_irrev_ms": 120000, "permit": "local", "extent": {"kind": "ticks", "ticks": 60}, "beacon": false, "while_unattended": "permit"}

actuate(tool, eff) := {
	"action": "Actuate",
	"principal": {"seat": "t1", "domain": "run", "kind": "thinker"},
	"resource": {"tool": tool, "digest": "d", "effect": eff},
	"inputs": {},
	"context": {"plane": "ap1", "planeKind": "autonomous"},
}

test_flight_entry_passes if {
	bundle.allow with input as actuate("flight.orbit", effect)
}

test_consult_passes if {
	bundle.allow with input as {"action": "Consult", "principal": {"seat": "t1", "domain": "run", "kind": "thinker"}, "resource": {"object": "maps"}, "context": {"plane": "ap1"}}
}

test_unknown_plane_refused if {
	not bundle.allow with input as {"action": "Consult", "principal": {"kind": "thinker"}, "context": {"plane": "ap9"}}
}

test_missing_plane_refused if {
	not bundle.allow with input as {"action": "Consult", "principal": {"kind": "thinker"}, "context": {}}
}

test_tool_outside_namespaces_refused if {
	not bundle.allow with input as actuate("stores.jettison", effect)
}

test_release_seat_refused if {
	not bundle.allow with input as {"action": "Report", "principal": {"kind": "release"}, "resource": {"kind": "round"}, "context": {"plane": "ib1"}}
}

test_irreversible_refused if {
	irrev := object.union(effect, {"class": "irreversible", "permit": "ordered"})
	not bundle.allow with input as actuate("flight.orbit", irrev)
}

test_no_effect_part_refused if {
	inp := {
		"action": "Actuate",
		"principal": {"kind": "thinker"},
		"resource": {"tool": "flight.orbit", "digest": "d"},
		"context": {"plane": "ap1"},
	}
	not bundle.allow with input as inp
}

test_no_extent_refused if {
	not bundle.allow with input as actuate("flight.orbit", object.remove(effect, ["extent"]))
}
