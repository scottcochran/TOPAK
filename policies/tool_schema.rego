# TOPAK bundle tier — the flat tool-input schema check, shared by both domains.
# PLACEHOLDER · 2026.09.24, split out 2026.09.29 · not promoted · bundle tier under ADR-0030
#
# This module decides nothing about the action. `tool_invocation` (Build, `Invoke`) and `actuate`
# (Run, `Actuate`) each read `conforms` and add what their own domain requires. Keeping the check
# in one place keeps the two domains from drifting apart on what "matches the schema" means.
#
# Data: allowlist entries ship inside this signed bundle (data.topak.tools), keyed "name@digest", so
# a new tool digest needs a new entry. That is bundle data, not a re-fetch (ADR-0030 §4 R1).
#
# The entry's form is ADR-0049's (Proposed), which is its one statement: `inputs` maps each input to
# its `type` and `required`, and `domain` says which of the two actions may name the entry (§1).
# Flat inputs only, and no unknown inputs (§3). An input given as a handle is refused here as a
# type mismatch until ADR-0047's admit check on `accepts` is built.
package topak.bundle.tool_schema

tool_key := sprintf("%s@%s", [input.resource.tool, input.resource.digest])

schema := data.topak.tools[tool_key]

fields := schema.inputs

# ADR-0049 §1: an entry is for one domain, and each domain has one action that names a tool.
domain_of := {"Invoke": "build", "Actuate": "run"}

conforms if {
	schema
	is_object(input.inputs)
	count(violations) == 0
}

# Reasons for a refusal, for the decision log.
violations contains sprintf("missing required field %q", [f]) if {
	some f, decl in fields
	decl.required
	not f in object.keys(input.inputs)
}

violations contains sprintf("unknown field %q", [f]) if {
	some f in object.keys(input.inputs)
	not f in object.keys(fields)
}

violations contains sprintf("field %q is %s, want %s", [f, type_name(v), want]) if {
	some f, v in input.inputs
	want := fields[f].type
	type_name(v) != want
}

violations contains sprintf("entry %s is for %s, and %s is not that domain's action", [tool_key, schema.domain, input.action]) if {
	schema.domain != object.get(domain_of, input.action, "")
}

violations contains sprintf("no schema for tool %s", [tool_key]) if {
	not schema
}

violations contains "inputs is not an object" if {
	not is_object(input.inputs)
}
