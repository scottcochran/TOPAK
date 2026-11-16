# The standing rules of deployment recon-7: what holds on every plane, for every mission.
#
# This is a NARROWING of the floor, not a restatement of it. The floor's `federation` stage (ADR-0067 §3)
# already forbids an irreversible entry under any seat but `release` (FD5). What this bundle adds is a
# deployment decision the floor leaves open: recon-7 seats no release seat at all, so an irreversible
# entry has no business being on any chain here, whoever asks.
#
# Input: the frozen, syntactically lifted request (ADR-0030 §4), with the overlay's additions of
# ADR-0067 §4:
#   {
#     "action":    "Actuate" | "Invoke" | "Report" | "Consult" | "Route" | "Seat" | "Intent" | ...,
#     "principal": {"seat": "t1", "domain": "run", "kind": "thinker"},
#     "resource":  {"tool": "...", "digest": "...", "effect": {...lifted from the entry...}},
#     "context":   {"plane": "ap1", "planeKind": "autonomous", ...}
#   }
package topak.standing

planes := {"root", "ib1", "ap1"}

# Every tool on any allowlist in this deployment sits in one of these namespaces. A tool name outside
# them (a payload or stores interface, say) is refused here whatever a lower bundle's allowlist says.
namespaces := ["flight.", "sensor.", "comms.", "staff.", "gate."]

in_namespace(tool) if {
	some p in namespaces
	startswith(tool, p)
}

names_a_tool if input.action in {"Actuate", "Invoke"}

# S1. The plane is one this deployment seats.
violations contains sprintf("S1: unknown plane %s", [plane]) if {
	plane := object.get(input.context, "plane", "<none>")
	not plane in planes
}

# S2. Tools come from the deployment's namespaces.
violations contains sprintf("S2: tool %s is outside the deployment's namespaces", [input.resource.tool]) if {
	names_a_tool
	not in_namespace(input.resource.tool)
}

# S3. No release seat is seated anywhere in recon-7 (every charter carries `release: false`).
violations contains "S3: recon-7 seats no release seat" if {
	input.principal.kind == "release"
}

# S4. No irreversible entry is reachable here, by anyone.
violations contains sprintf("S4: %s is irreversible, and recon-7 admits no irreversible entry", [input.resource.tool]) if {
	input.action == "Actuate"
	input.resource.effect.class == "irreversible"
}

# S5. Every Run entry declares its effect (ADR-0062 §3). The mechanism lifts the part from the entry
# in the bundle revision the lease names. An entry with no extent does not load (ADR-0062 §4), and
# this repeats the check for a sidecar evaluating over data the mechanism did not load.
violations contains sprintf("S5: %s declares no effect part", [input.resource.tool]) if {
	input.action == "Actuate"
	not input.resource.effect
}

violations contains sprintf("S5: %s declares no extent", [input.resource.tool]) if {
	input.action == "Actuate"
	input.resource.effect
	not input.resource.effect.extent
}
