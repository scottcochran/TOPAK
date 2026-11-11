# The command rules of deployment recon-7: what the intent boundary may hand down, and who routes.
#
# Three acts are narrowed. `Route` is the workflow action (ADR-0054 §3). `Seat` and `Intent` are the
# overlay's: the seating of a plane under a charter (ADR-0059 §1), and a commander's grant of one
# round to an autonomous plane (ADR-0060 §2). The floor's FD1 refuses whatever exceeds the bound the
# parent set. These rules are tighter, and are this deployment's choices: one fleet, one 24-hour
# envelope, and a person at every go/no-go.
#
# Overlay input for the two new actions. `input.request` is the typed act, as the lift froze it.
#   Seat:   {"plane": "ap1", "kind": "autonomous", "release": false}
#   Intent: {"plane": "ap1", "round": 1, "expiry": {"from_tick": 0, "ticks": 2879}, "budget": 112}
package topak.command

# The one child plane this intent boundary may seat. Single fleet, so no sibling planes, which also
# keeps this deployment out of the open question of overlapping sibling envelopes (ADR-0067).
child := "ap1"

# 24 hours at T_tick = 30 s is 2880 periods. A replica signs no grant while the next tick is due, so a
# grant at tick c happens before real time (c + 1) · T_tick (ADR-0064 §4). The last tick that keeps
# every grant inside 24 hours, on that section's premise, is 2879.
max_expiry_tick := 2879

max_budget := 112

# Chosen edges of the promoted staff DAG (2-workflows/staff-cycle.dag.json). A person holds them ⟨Q10⟩.
chosen_edges := {"e-go", "e-scrub"}

route_seat := "orc-co"

operator_seats := {"op1", "op2", "op3"}

at_ib if input.context.plane == "ib1"

# ---- Route --------------------------------------------------------------------------------------

violations contains "C1: at ib1 only a person routes" if {
	at_ib
	input.action == "Route"
	input.principal.actor != "person"
}

violations contains sprintf("C1: seat %s does not hold the go/no-go", [input.principal.seat]) if {
	at_ib
	input.action == "Route"
	input.principal.seat != route_seat
}

violations contains sprintf("C1: %s is not a chosen edge of the staff DAG", [input.resource.edge]) if {
	at_ib
	input.action == "Route"
	not input.resource.edge in chosen_edges
}

# ---- Seat ---------------------------------------------------------------------------------------

violations contains sprintf("C2: ib1 seats only %s", [child]) if {
	at_ib
	input.action == "Seat"
	input.request.plane != child
}

violations contains "C2: the plane below ib1 is autonomous" if {
	at_ib
	input.action == "Seat"
	input.request.kind != "autonomous"
}

violations contains "C2: no plane in recon-7 carries release" if {
	input.action == "Seat"
	object.get(input.request, "release", false) != false
}

violations contains "C2: the fleet's plane is already seated" if {
	at_ib
	input.action == "Seat"
	input.context.childrenSeated >= 1
}

# ---- Intent -------------------------------------------------------------------------------------

violations contains sprintf("C3: an intent is issued at ib1, and this request is at %s", [input.context.plane]) if {
	input.action == "Intent"
	not at_ib
}

violations contains sprintf("C3: seat %s is not an operator of ib1", [input.principal.seat]) if {
	at_ib
	input.action == "Intent"
	not input.principal.seat in operator_seats
}

# ⟨Q4⟩ bounds a later intent by the promoted seating and not by the last intent, so the end of the
# envelope is an absolute tick: a later intent may start late, and may not end late.
violations contains "C3: the intent ends after the 24-hour envelope" if {
	at_ib
	input.action == "Intent"
	input.request.expiry.from_tick + input.request.expiry.ticks > max_expiry_tick
}

violations contains "C3: the intent's budget exceeds the seating's" if {
	at_ib
	input.action == "Intent"
	input.request.budget > max_budget
}

violations contains "C3: an intent cannot name a release seat" if {
	input.action == "Intent"
	object.get(input.request, "release", false) != false
}
