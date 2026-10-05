# TOPAK bundle tier — Run's `Actuate` check.
# PLACEHOLDER · 2026.09.29 · not promoted · bundle tier under ADR-0030 · ADR-0041 §5 (Proposed)
#
# A bundle can only narrow (ADR-0030 §1). The floor already decided the tool is allowlisted by
# name and digest, or is inside the break-glass envelope (floor R1, X1). This policy refuses an
# `Actuate` when either of two things is wrong:
#
#   1. its inputs do not match the tool's declared schema, as for `Invoke`;
#   2. the tool's entry declares no effect channel.
#
# The second is Run's. A Run tool is not hermetic and is not asked to be; it is asked to open the
# channel its allowlist entry declares and no other (ADR-0040 §3). An entry that declares nothing
# gives the Run profile and the Observer nothing to hold the tool to, so it is refused here.
#
# The channel's form is ADR-0049's (Proposed): an object with two non-empty strings.
#
#     "channel": {"kind": "https", "target": "search.internal:443"}
#
# The mechanism refuses a bundle whose Run entry lacks one when it loads the bundle (ADR-0049 W4).
# The check is repeated here because a sidecar evaluates this policy over data the mechanism did
# not load. `kind` is DECLARED, NOT INTERPRETED. `target` is where the tool host binds a Wasm
# tool's one connection (ADR-0034 A2); for a native tool it is an assertion (G19).
#
# Input: the frozen, syntactically lifted request (ADR-0030 §4).
#   {
#     "action":    "Actuate",
#     "principal": {"seat": "r1", "domain": "run"},
#     "resource":  {"tool": "search", "digest": "d3"},
#     "inputs":    { ...tool arguments... }
#   }
package topak.bundle.actuate

import data.topak.bundle.tool_schema

default allow := false

allow if {
	input.action == "Actuate"
	tool_schema.conforms
	count(channel_violations) == 0
}

channel := tool_schema.schema.channel

nonempty_string(v) if {
	is_string(v)
	count(v) > 0
}

channel_violations contains sprintf("tool %s declares no effect channel", [tool_schema.tool_key]) if {
	tool_schema.schema
	not tool_schema.schema.channel
}

channel_violations contains "channel is not an object" if {
	not is_object(channel)
}

channel_violations contains sprintf("channel.%s is missing or empty", [k]) if {
	is_object(channel)
	some k in {"kind", "target"}
	not nonempty_string(object.get(channel, k, null))
}

channel_violations contains sprintf("channel has an unknown field %q", [k]) if {
	is_object(channel)
	some k in object.keys(channel)
	not k in {"kind", "target"}
}

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := tool_schema.violations | channel_violations
