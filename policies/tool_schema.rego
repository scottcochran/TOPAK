# TOPAK bundle tier — the flat tool-input schema check, shared by both domains.
# PLACEHOLDER · 2026.09.24, split out 2026.09.29 · not promoted · bundle tier under ADR-0030
#
# This module decides nothing about the action. `tool_invocation` (Build, `Invoke`) and `actuate`
# (Run, `Actuate`) each read `conforms` and add what their own domain requires. Keeping the check
# in one place keeps the two domains from drifting apart on what "matches the schema" means.
#
# Data: tool schemas ship inside this signed bundle (data.topak.tools), keyed "name@digest", so a
# new tool digest needs a new schema entry. That is bundle data, not a re-fetch (ADR-0030 §4 R1).
#
# Placeholder scope: flat objects only — required fields, optional fields, a type per field, and
# no unknown fields. Nested schemas, value ranges and formats are future work.
package topak.bundle.tool_schema

tool_key := sprintf("%s@%s", [input.resource.tool, input.resource.digest])

schema := data.topak.tools[tool_key]

fields := object.union(schema.required, object.get(schema, "optional", {}))

conforms if {
	schema
	is_object(input.inputs)
	count(violations) == 0
}

# Reasons for a refusal, for the decision log.
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
