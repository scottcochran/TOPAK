# TOPAK bundle tier, deployment recon-7: the COMMAND bundle. Entrypoint.
# Promoted at the root plane with the seating of ib1, and so on the chains of ib1 and ap1.
# ILLUSTRATIVE · 2026.11.10 · not promoted · a use-case configuration under ADR-0030 and ADR-0059 §2 (Proposed)
#
# It narrows the acts of a commanded plane. It sits on ap1's chain too, because a charter's bundle
# list only grows (ADR-0059 §1), so every tool check here is scoped to a commanded plane: this
# bundle's allowlist knows nothing of the vehicles' entries, which are the mission bundle's, and an
# unscoped schema check would refuse every one of them. Actions no module narrows pass at the floor.
package topak.bundle

import data.topak.bundle.actuate
import data.topak.bundle.tool_invocation
import data.topak.command

default allow := false

allow if not refused

commanded if input.context.planeKind == "commanded"

# Build at a commanded plane: the mission package's gate tools match their declared schema.
refused if {
	commanded
	input.action == "Invoke"
	not tool_invocation.allow
}

# Run at a commanded plane: staff tools match their schema and declare a channel.
refused if {
	commanded
	input.action == "Actuate"
	not actuate.allow
}

refused if count(command.violations) > 0

# Reasons for a refusal, for the decision log. `allow` is what the mechanism reads.
violations := command.violations
