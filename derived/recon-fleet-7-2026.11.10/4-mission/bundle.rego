# TOPAK bundle tier, deployment recon-7: the MISSION bundle, MSN-0001. Entrypoint.
# Voted at ib1 by digest in one tally with the mesh and ap1's charter (ADR-0060 §5). Last on ap1's
# chain, and the revision each vehicle's lease names. Evaluated in Wasm on all seven governors and at
# ap1's replicas (ADR-0067 §2).
# ILLUSTRATIVE · 2026.11.10 · not promoted · a use-case configuration under ADR-0030 and ADR-0067 (Proposed)
#
# plan.rego is the mission plan, roe.rego the rules of engagement, geo.rego their arithmetic. data.json
# carries the allowlist (ADR-0049 with the `effect` part of ADR-0062 §3) and the peer topics.
package topak.bundle

import data.topak.bundle.actuate
import data.topak.mission.roe

default allow := false

allow if not refused

autonomous if input.context.planeKind == "autonomous"

# Every vehicle entry matches its declared schema and channel.
refused if {
	autonomous
	input.action == "Actuate"
	not actuate.allow
}

refused if count(roe.violations) > 0

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := roe.violations | actuate.violations
