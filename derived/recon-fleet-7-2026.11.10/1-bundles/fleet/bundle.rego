# TOPAK bundle tier, deployment recon-7: the FLEET bundle. Entrypoint.
# Promoted at ib1 with the mission, on ap1's chain only. Evaluated in Wasm on all seven governors and
# at ap1's replicas (ADR-0067 §2).
# ILLUSTRATIVE · 2026.11.10 · not promoted · a use-case configuration under ADR-0030 and ADR-0062 (Proposed)
#
# It holds what is true of this vehicle class on any mission: the mission bundle changes per tasking,
# and this one changes when the airframe does.
package topak.bundle

import data.topak.fleet

default allow := false

allow if not refused

refused if count(fleet.violations) > 0

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := fleet.violations
