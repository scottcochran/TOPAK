# TOPAK bundle tier, deployment recon-7: the STANDING bundle. Entrypoint.
# Promoted at the root plane. First on every chain: root, ib1 and ap1 all evaluate it.
# ILLUSTRATIVE · 2026.11.10 · not promoted · a use-case configuration under ADR-0030 and ADR-0067 (Proposed)
#
# The mechanism evaluates `data.topak.bundle.allow` and admits iff floor_permit ∧ ¬bundle_deny, and
# anything but an affirmative `true` is a deny (ADR-0030 §1). This bundle can only refuse.
package topak.bundle

import data.topak.standing

default allow := false

allow if not refused

refused if count(standing.violations) > 0

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := standing.violations
