package topak.bundle_test

import data.topak.bundle

test_read_passes_through if {
	bundle.allow with input as {"action": "Read", "principal": {"seat": "a1", "domain": "build"}, "resource": {"object": "x"}}
}

test_conforming_invoke_allowed if {
	bundle.allow with input as {
		"action": "Invoke",
		"principal": {"seat": "a1", "domain": "build"},
		"resource": {"tool": "tlc", "digest": "d1"},
		"inputs": {"spec": "Lease.tla", "config": "Lease.cfg"},
	}
}

test_nonconforming_invoke_refused if {
	not bundle.allow with input as {
		"action": "Invoke",
		"principal": {"seat": "a1", "domain": "build"},
		"resource": {"tool": "tlc", "digest": "d1"},
		"inputs": {"spec": "Lease.tla"},
	}
}

test_unknown_tool_refused if {
	not bundle.allow with input as {
		"action": "Actuate",
		"principal": {"seat": "r1", "domain": "run"},
		"resource": {"tool": "curl", "digest": "d9"},
		"inputs": {},
	}
}

test_conforming_actuate_allowed if {
	bundle.allow with input as {
		"action": "Actuate",
		"principal": {"seat": "r1", "domain": "run"},
		"resource": {"tool": "search", "digest": "d3"},
		"inputs": {"query": "lease schema"},
	}
}

# A Build tool's entry declares no channel, so it cannot be actuated even if a floor allowlisted it.
test_actuate_of_a_tool_with_no_channel_refused if {
	not bundle.allow with input as {
		"action": "Actuate",
		"principal": {"seat": "r1", "domain": "run"},
		"resource": {"tool": "tlc", "digest": "d1"},
		"inputs": {"spec": "Lease.tla", "config": "Lease.cfg"},
	}
}

# No module narrows Consult or Report: they pass at the floor (ADR-0041 §5).
test_consult_passes_through if {
	bundle.allow with input as {"action": "Consult", "principal": {"seat": "r1", "domain": "run"}, "resource": {"object": "x"}}
}

test_report_passes_through if {
	bundle.allow with input as {"action": "Report", "principal": {"seat": "r1", "domain": "run"}, "resource": {"topic": "t"}}
}
