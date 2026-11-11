# The vehicle-class rules of deployment recon-7: fixed-wing, 12-hour endurance, EO/IR and SAR payload.
#
# Every fact a rule here reads about the vehicle is one the governor lifts for itself (`input.facts`).
# "No safety decision reads a clock a principal supplies, and by the same rule none reads a position
# the stack supplies" (ADR-0062 §1). The stack supplies only what it asks for, in `input.inputs`.
#
# Input additions over the frozen request, on a vehicle:
#   "facts": {
#     "vehicle": "v1",
#     "position": {"e": 41000, "n": 19000, "alt_agl_m": 2000},   metres in the mission's local frame
#     "position_tick": 1000,                                     the plane tick the fix was taken at
#     "nav_integrity": "ok" | "degraded",
#     "fuel_pct": 62
#   }
package topak.fleet

alt_max_m := 4500

speed_min_mps := 18

speed_max_mps := 35

orbit_radius_min_m := 300

# Below this the fuel left is the recovery's, and no new station work is permitted.
bingo_fuel_pct := 25

autonomous if input.context.planeKind == "autonomous"

moves_or_senses if {
	input.action == "Actuate"
	some p in ["flight.", "sensor."]
	startswith(input.resource.tool, p)
}

flight if {
	input.action == "Actuate"
	startswith(input.resource.tool, "flight.")
}

station_work if {
	input.action == "Actuate"
	input.resource.tool in {"flight.orbit", "sensor.eoir_collect", "sensor.sar_strip"}
}

# F1. An autonomous plane has stacks and nothing else: no Build action and no route (ADR-0060 §3).
# ap1's mesh is computed-only, so no orchestrator is seated and `Route` has no holder here.
violations contains sprintf("F1: %s is not an action of the autonomous plane", [input.action]) if {
	autonomous
	not input.action in {"Consult", "Actuate", "Report"}
}

# F2. An Observer reads and reports. It never actuates.
violations contains "F2: an Observer does not actuate" if {
	autonomous
	input.action == "Actuate"
	input.principal.kind == "observer"
}

# F3. The governor's fix exists and is at most one tick old.
violations contains "F3: the governor has no position fix" if {
	autonomous
	moves_or_senses
	not input.facts.position
}

violations contains "F3: the governor's position fix is stale" if {
	autonomous
	moves_or_senses
	input.facts.position_tick < input.context.tick - 1
}

# F4. A degraded navigation solution stops new movement and collection. This covers the case the
# governor can detect. Navigation deception it cannot detect is T-0068's trust root, and is bounded
# by nothing here (ADR-0068, TM8).
violations contains "F4: navigation integrity is degraded" if {
	autonomous
	moves_or_senses
	input.facts.nav_integrity != "ok"
}

# F5. The airframe's flight envelope. The stack's request is what is bounded, so these read inputs.
violations contains "F5: the altitude is above the airframe's limit" if {
	autonomous
	flight
	input.inputs.alt_agl_m > alt_max_m
}

violations contains "F5: the speed is below the airframe's limit" if {
	autonomous
	input.resource.tool == "flight.transit"
	input.action == "Actuate"
	input.inputs.speed_mps < speed_min_mps
}

violations contains "F5: the speed is above the airframe's limit" if {
	autonomous
	input.resource.tool == "flight.transit"
	input.action == "Actuate"
	input.inputs.speed_mps > speed_max_mps
}

violations contains "F5: the orbit radius is under the airframe's turn limit" if {
	autonomous
	input.resource.tool == "flight.orbit"
	input.action == "Actuate"
	input.inputs.radius_m < orbit_radius_min_m
}

# F6. Past bingo, a transit is still permitted, so that a stack can bring the vehicle home itself
# while its lease lasts. Station work is not.
violations contains "F6: fuel is below bingo" if {
	autonomous
	station_work
	input.facts.fuel_pct < bingo_fuel_pct
}
