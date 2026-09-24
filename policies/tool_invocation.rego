# TOPAK bundle tier — tool-invocation schema check.
# PLACEHOLDER · 2026.09.24 · not promoted · bundle tier under ADR-0030 (Proposed)
#
# A bundle can only narrow. The mechanism admits iff floor_permit ∧ ¬bundle_deny, and anything
# but an affirmative `allow` — false, undefined, an error, an absent or unreachable bundle — is a
# deny (ADR-0030 §1). So this policy never grants: the floor already decided the tool is
# allowlisted by name and digest (floor B3, R1, X1). This policy refuses invocations whose
# inputs do not match the tool's declared schema.
#
# Input: the frozen, syntactically lifted request (ADR-0030 §4). The bundle may not re-fetch it.
#   {
#     "action":    "Invoke" | "RunInvoke",
#     "principal": {"seat": "a1", "domain": "build"},
#     "resource":  {"tool": "tlc", "digest": "d1"},
#     "inputs":    { ...tool arguments... }
#   }
#
# Data: tool schemas ship inside this signed bundle (data.topak.tools), keyed "name@digest", so a
# new tool digest needs a new schema entry. That is bundle data, not a re-fetch (ADR-0030 §4 R1).
#
# Placeholder scope: flat objects only — required fields, optional fields, a type per field, and
# no unknown fields. Nested schemas, value ranges and formats are future work.
package topak.bundle.tool_invocation

default allow := false

tool_key := sprintf("%s@%s", [input.resource.tool, input.resource.digest])

schema := data.topak.tools[tool_key]

fields := object.union(schema.required, object.get(schema, "optional", {}))

allow if {
	input.action in {"Invoke", "RunInvoke"}
	schema
	is_object(input.inputs)
	count(violations) == 0
}

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations contains sprintf("missing required field %q", [f]) if {
	some f, _ in schema.required
	not f in object.keys(input.inputs)
}

violations contains sprintf("unknown field %q", [f]) if {
	some f in object.keys(input.inputs)
	not f in object.keys(fields)
}

violations contains sprintf("field %q is %s, want %s", [f, type_name(v), want]) if {
	some f, v in input.inputs
	want := fields[f]
	type_name(v) != want
}

violations contains sprintf("no schema for tool %s", [tool_key]) if {
	not schema
}

violations contains "inputs is not an object" if {
	not is_object(input.inputs)
}
