package topak.bundle.tool_invocation_test

import data.topak.bundle.tool_invocation

tlc(inputs) := {
	"action": "Invoke",
	"principal": {"seat": "a1", "domain": "build"},
	"resource": {"tool": "tlc", "digest": "d1"},
	"inputs": inputs,
}

good := {"spec": "Lease.tla", "config": "Lease.cfg", "workers": 4}

test_conforming_inputs_allowed if {
	tool_invocation.allow with input as tlc(good)
}

test_required_only_allowed if {
	tool_invocation.allow with input as tlc({"spec": "Lease.tla", "config": "Lease.cfg"})
}

test_run_invoke_allowed if {
	tool_invocation.allow with input as {
		"action": "RunInvoke",
		"resource": {"tool": "search", "digest": "d3"},
		"inputs": {"query": "lease schema"},
	}
}

test_missing_required_denied if {
	not tool_invocation.allow with input as tlc({"spec": "Lease.tla"})
	"missing required field \"config\"" in tool_invocation.violations with input as tlc({"spec": "Lease.tla"})
}

test_unknown_field_denied if {
	inp := object.union(good, {"shell": "sh -c ..."})
	not tool_invocation.allow with input as tlc(inp)
	"unknown field \"shell\"" in tool_invocation.violations with input as tlc(inp)
}

test_wrong_type_denied if {
	inp := object.union(good, {"workers": "4"})
	not tool_invocation.allow with input as tlc(inp)
	"field \"workers\" is string, want number" in tool_invocation.violations with input as tlc(inp)
}

test_unknown_digest_denied if {
	inp := object.union(tlc(good), {"resource": {"tool": "tlc", "digest": "d2"}})
	not tool_invocation.allow with input as inp
	"no schema for tool tlc@d2" in tool_invocation.violations with input as inp
}

test_inputs_not_object_denied if {
	not tool_invocation.allow with input as tlc(["Lease.tla"])
}

test_other_action_denied if {
	not tool_invocation.allow with input as object.union(tlc(good), {"action": "Emit"})
}

test_malformed_request_denied if {
	not tool_invocation.allow with input as {"action": "Invoke"}
}
