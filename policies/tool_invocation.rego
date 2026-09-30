# TOPAK bundle tier — Build's tool-invocation check.
# PLACEHOLDER · 2026.09.24, Build-only since 2026.09.29 · not promoted · bundle tier under ADR-0030
#
# A bundle can only narrow. The mechanism admits iff floor_permit ∧ ¬bundle_deny, and anything
# but an affirmative `allow` — false, undefined, an error, an absent or unreachable bundle — is a
# deny (ADR-0030 §1). So this policy never grants: the floor already decided the tool is
# allowlisted by name and digest (floor B3). This policy refuses invocations whose inputs do not
# match the tool's declared schema.
#
# Run's tools are `actuate.rego`'s. `Invoke` and `Actuate` share a schema check and nothing else:
# a Build tool is hermetic (ADR-0022 §3) and a Run tool opens a channel (ADR-0040 §3).
#
# Input: the frozen, syntactically lifted request (ADR-0030 §4). The bundle may not re-fetch it.
#   {
#     "action":    "Invoke",
#     "principal": {"seat": "a1", "domain": "build"},
#     "resource":  {"tool": "tlc", "digest": "d1"},
#     "inputs":    { ...tool arguments... }
#   }
package topak.bundle.tool_invocation

import data.topak.bundle.tool_schema

default allow := false

allow if {
	input.action == "Invoke"
	tool_schema.conforms
}

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := tool_schema.violations
