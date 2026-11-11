# MISSION PLAN, MSN-0001 · deployment recon-7 · promoted with the mission bundle at ib1 (ADR-0060 §5)
# ILLUSTRATIVE · 2026.11.10 · not promoted
#
# A plan, in the only sense a bundle can hold one: facts the ROE compares a request against. The plan
# grants nothing. A vehicle outside it is refused. A vehicle inside it is merely not refused by this
# module, and still needs its lease, the floor and every other bundle on the chain.
#
# TASK. Persistent wide-area reconnaissance of three sectors (A north, B centre, C south) for one
# 24-hour intent, with continuous coverage from H+0:30 to H+22:30.
#
# TIME. Every time is a tick of plane ap1 (ADR-0064 §3): T_tick = 30 s, so 120 ticks is one hour.
# Tick zero is the application of ap1's charter ⟨Q13⟩, and not the vote or any wall clock.
#
#              launch  on station    relief out   recover by    A    B    C
#     W1          20   60  -  1020     (H+8:30)      1100      v1   v2   v3
#     W2         920  960  -  1920     (H+16:00)     2000      v4   v5   v6
#     W3        1820 1860  -  2700     (H+22:30)     2780      v1   v2   v3
#     spare       20   60  -  2700                   2780      v7, any sector
#
# Each relief overlaps the outgoing wave by 60 ticks (30 min) on station. v1 to v3 turn around for
# 720 ticks (6 h) between W1 and W3. No sortie exceeds 1080 ticks (9 h) against 12 h of endurance.
#
# SPACE. Planar metres east and north of the recovery site R1 at (0, 0), so the plan names no real
# place. A deployment maps the frame to a datum in the governor's navigation configuration.
package topak.mission.plan

mission_id := "MSN-0001"

# The last valid tick. See command.rego for why 24 hours is 2879 and not 2880.
intent := {"from_tick": 0, "expiry_tick": 2879, "tick_ms": 30000}

waves := {
	"W1": {"launch": 20, "station_from": 60, "station_to": 1020, "recover_by": 1100, "assignments": {"v1": "A", "v2": "B", "v3": "C"}},
	"W2": {"launch": 920, "station_from": 960, "station_to": 1920, "recover_by": 2000, "assignments": {"v4": "A", "v5": "B", "v6": "C"}},
	"W3": {"launch": 1820, "station_from": 1860, "station_to": 2700, "recover_by": 2780, "assignments": {"v1": "A", "v2": "B", "v3": "C"}},
}

spare := {"vehicle": "v7", "launch": 20, "station_from": 60, "station_to": 2700, "recover_by": 2780, "sectors": {"A", "B", "C"}}

operating_area := [[-5000, -30000], [70000, -30000], [70000, 30000], [-5000, 30000]]

# The launch and recovery lanes. Overlaps each sector by 2 km so a transit can end inside it.
ingress := [[-5000, -30000], [22000, -30000], [22000, 30000], [-5000, 30000]]

sectors := {
	"A": [[20000, 11000], [60000, 11000], [60000, 28000], [20000, 28000]],
	"B": [[20000, -8000], [60000, -8000], [60000, 7000], [20000, 7000]],
	"C": [[20000, -28000], [60000, -28000], [60000, -10000], [20000, -10000]],
}

altitude := {
	"transit": {"min_agl_m": 600, "max_agl_m": 3048},
	"station": {"min_agl_m": 1500, "max_agl_m": 3048},
}

# Flight is prohibited inside these. NFZ-CLINIC sits in the 4 km gap between sectors A and B, so that
# the straight recovery leg from any point of either sector stays clear of it.
no_fly := {
	"NFZ-CLINIC": {"shape": "circle", "centre": {"e": 40000, "n": 9000}, "radius_m": 1500},
	"NFZ-AIRFIELD": {"shape": "poly", "points": [[5000, 12000], [12000, 12000], [12000, 20000], [5000, 20000]]},
}

# A sensor may not be aimed so that its footprint reaches these.
no_collect := {
	"NCZ-SITE-1": {"shape": "circle", "centre": {"e": 35000, "n": 18000}, "radius_m": 2500},
	"NCZ-CLINIC": {"shape": "circle", "centre": {"e": 40000, "n": 9000}, "radius_m": 2000},
}

footprint_margin_m := 800

# Radio silence: no peer report, no downlink and no beacon originates inside this.
quiet_zones := {"QZ-SOUTH": {"shape": "poly", "points": [[20000, -28000], [60000, -28000], [60000, -23000], [20000, -23000]]}}

separation := {"horizontal_m": 1000, "vertical_m": 150, "max_fix_age_ticks": 2}

in_intent(t) if {
	t >= intent.from_tick
	t < intent.expiry_tick
}

# The sector a vehicle may work at a tick, and the sector it is sortied against.
on_station(v, t, s) if {
	some w in waves
	t >= w.station_from
	t < w.station_to
	w.assignments[v] == s
}

on_station(v, t, s) if {
	v == spare.vehicle
	t >= spare.station_from
	t < spare.station_to
	s in spare.sectors
}

sortie_active(v, t) if {
	some w in waves
	t >= w.launch
	t < w.recover_by
	w.assignments[v]
}

sortie_active(v, t) if {
	v == spare.vehicle
	t >= spare.launch
	t < spare.recover_by
}

in_sortie(v, t, s) if {
	some w in waves
	t >= w.launch
	t < w.recover_by
	w.assignments[v] == s
}

in_sortie(v, t, s) if {
	v == spare.vehicle
	t >= spare.launch
	t < spare.recover_by
	s in spare.sectors
}
