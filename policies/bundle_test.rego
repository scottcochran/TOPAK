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
		"action": "RunInvoke",
		"principal": {"seat": "r1", "domain": "run"},
		"resource": {"tool": "curl", "digest": "d9"},
		"inputs": {},
	}
}
