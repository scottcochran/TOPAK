# TOPAK bundle tier — the entrypoint the mechanism reads.
# PLACEHOLDER · 2026.09.24 · not promoted · bundle tier under ADR-0030 (Proposed)
#
# The mechanism evaluates `data.topak.bundle.allow` and admits iff
#   floor_permit ∧ ¬bundle_deny
# where anything but an affirmative `true` here is a deny (ADR-0030 §1). The bundle is
# consulted only after the floor has permitted, so it can only refuse: it is never asked
# whether to grant.
#
# `allow` is therefore "nothing refuses". Each module contributes a refusal condition for the
# actions it narrows; actions no module narrows pass at the floor.
#
# Input: the frozen, syntactically lifted request (ADR-0030 §4), identical for the sidecar and
# the local WASM fallback:
#   {
#     "action":    "Read" | "Draft" | "Invoke" | "Emit" | "Submit" | "Vote"     (Build, ADR-0022 §1)
#                | "Consult" | "Actuate" | "Report"                            (Run, ADR-0040 §1),
#     "principal": {"seat": "a1", "domain": "build"},
#     "resource":  {...action-specific; Invoke: {"tool": ..., "digest": ...}},
#     "inputs":    {...tool arguments, Invoke and Actuate only...},
#     "request":   {...the typed action...},
#     "context":   {"epoch", "round", "roundRole", "rulesEpoch", "lease"}
#   }
package topak.bundle

import data.topak.bundle.actuate
import data.topak.bundle.tool_invocation

default allow := false

allow if not refused

# Build: a tool invocation must match the tool's declared input schema.
refused if {
	input.action == "Invoke"
	not tool_invocation.allow
}

# Run: an actuation must match the schema, and its tool must declare an effect channel
# (ADR-0041 §5; ADR-0040 §3).
refused if {
	input.action == "Actuate"
	not actuate.allow
}
