package topak.bundle.actuate_test

import data.topak.bundle.actuate

search(inputs) := {
	"action": "Actuate",
	"principal": {"seat": "r1", "domain": "run"},
	"resource": {"tool": "search", "digest": "d3"},
	"inputs": inputs,
}

good := {"query": "lease schema", "limit": 5}

tools(channel) := {"search@d3": {"required": {"query": "string"}, "optional": {"limit": "number"}, "channel": channel}}

test_conforming_actuate_allowed if {
	actuate.allow with input as search(good)
}

test_required_only_allowed if {
	actuate.allow with input as search({"query": "lease schema"})
}

test_missing_required_denied if {
	not actuate.allow with input as search({"limit": 5})
	"missing required field \"query\"" in actuate.violations with input as search({"limit": 5})
}

test_unknown_field_denied if {
	inp := object.union(good, {"url": "https://elsewhere.example"})
	not actuate.allow with input as search(inp)
	"unknown field \"url\"" in actuate.violations with input as search(inp)
}

test_no_schema_denied if {
	inp := object.union(search(good), {"resource": {"tool": "search", "digest": "d9"}})
	not actuate.allow with input as inp
	"no schema for tool search@d9" in actuate.violations with input as inp
}

# ADR-0040 §3: a Run tool's entry declares the channel it opens. One that declares nothing is refused.
test_no_channel_denied if {
	t := {"search@d3": {"required": {"query": "string"}}}
	not actuate.allow with input as search({"query": "q"}) with data.topak.tools as t
	"tool search@d3 declares no effect channel" in actuate.violations with input as search({"query": "q"}) with data.topak.tools as t
}

test_channel_not_an_object_denied if {
	not actuate.allow with input as search(good) with data.topak.tools as tools("https://search.internal")
	"channel is not an object" in actuate.violations with input as search(good) with data.topak.tools as tools("https://search.internal")
}

test_channel_missing_target_denied if {
	not actuate.allow with input as search(good) with data.topak.tools as tools({"kind": "https"})
	"channel.target is missing or empty" in actuate.violations with input as search(good) with data.topak.tools as tools({"kind": "https"})
}

test_channel_empty_kind_denied if {
	c := {"kind": "", "target": "search.internal:443"}
	not actuate.allow with input as search(good) with data.topak.tools as tools(c)
	"channel.kind is missing or empty" in actuate.violations with input as search(good) with data.topak.tools as tools(c)
}

test_channel_unknown_field_denied if {
	c := {"kind": "https", "target": "search.internal:443", "also": "anything"}
	not actuate.allow with input as search(good) with data.topak.tools as tools(c)
	"channel has an unknown field \"also\"" in actuate.violations with input as search(good) with data.topak.tools as tools(c)
}

# Run's check is Run's: a conforming Build request is not its to allow.
test_invoke_is_not_actuate if {
	not actuate.allow with input as object.union(search(good), {"action": "Invoke"})
}

test_retired_name_denied if {
	not actuate.allow with input as object.union(search(good), {"action": "RunInvoke"})
}

test_malformed_request_denied if {
	not actuate.allow with input as {"action": "Actuate"}
}
