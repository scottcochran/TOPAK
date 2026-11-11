package topak.standing_test

import data.topak.standing

test_known_tool_permitted if {
	count(standing.violations) == 0 with input as {"action": "Actuate", "resource": {"tool": "example.lookup"}}
}

test_unknown_tool_refused if {
	"S1: the tool is not on the allowlist" in standing.violations with input as {"action": "Actuate", "resource": {"tool": "other"}}
}

test_orchestrator_routes if {
	count(standing.violations) == 0 with input as {"action": "Route", "principal": {"seat": "orc1"}}
}

test_another_seat_cannot_route if {
	"S2: only a person routes" in standing.violations with input as {"action": "Route", "principal": {"seat": "t1"}}
}
