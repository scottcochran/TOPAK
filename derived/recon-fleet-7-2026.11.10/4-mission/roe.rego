# RULES OF ENGAGEMENT, MSN-0001 · deployment recon-7 · promoted with the mission bundle at ib1 (ADR-0067 §2)
# ILLUSTRATIVE · 2026.11.10 · not promoted
#
# A reconnaissance mission. No entry on this mission's allowlist can harm anything: a vehicle flies,
# senses and transmits. Nothing here authorizes an effect. Each rule can only refuse (ADR-0030 §1).
#
# WHAT THIS FILE CANNOT SAY (ADR-0067 §6). The mechanical rules are here. Rules that need a judgment
# about the world are enforced by nothing in the admit path, and are carried by the commander's order
# and the operator's training:
#   - that a track is what the stack says it is;
#   - that the collection in an authorized sector is necessary and proportionate;
#   - that the no-collect and no-fly lists are complete. The rules below test the lists they are given.
#
# INPUT, as the governor or the plane lifts it. Who supplied what matters, because the stack is
# Byzantine: `input.inputs` is the stack's request; `input.facts` and `input.context` are the
# governor's and the plane's own.
#   "context": {"plane", "planeKind", "tick", "permittedBy": "governor"|"plane", "hearsPlane",
#               "ticksSinceWatermark", "clearSet", "sendsThisTick": {every declared topic: n}, "sendsThisLease",
#               "beaconsThisLease", "activeEmitters": {sector: n}}
#   "facts":   {"vehicle", "position": {"e","n","alt_agl_m"}, "peers": [{"vehicle","e","n","alt_agl_m","tick"}]}
#
# Refusal text uses sprintf with %s only, and only over strings. The reference's Wasm engine (opa-wasm)
# traps on %v and %q, which still denies but loses the reason, and a governor has no other engine.
package topak.mission.roe

import data.topak.mission.geo
import data.topak.mission.plan

topics := data.topak.topics

ticks_unattended := 60

sends_per_lease := 240

beacons_per_lease := 10

transit_extent_m := 40000

sar_extent_m := 20000

tick := input.context.tick

vehicle := input.facts.vehicle

pos := input.facts.position

args := input.inputs

autonomous if input.context.planeKind == "autonomous"

actuates(t) if {
	autonomous
	input.action == "Actuate"
	input.resource.tool == t
}

is_transit if actuates("flight.transit")

is_orbit if actuates("flight.orbit")

is_collect if actuates("sensor.eoir_collect")

is_sar if actuates("sensor.sar_strip")

is_downlink if actuates("comms.downlink")

is_beacon if actuates("comms.beacon")

is_flight if is_transit

is_flight if is_orbit

is_sensor if is_collect

is_sensor if is_sar

peer_report if {
	autonomous
	input.action == "Report"
	input.resource.kind == "peer"
}

target := {"e": args.e, "n": args.n}

sar_from := {"e": args.from_e, "n": args.from_n}

sar_to := {"e": args.to_e, "n": args.to_n}

sector_of(p) := s if {
	some s, poly in plan.sectors
	geo.in_poly(poly, p)
}

# ---- ROE-1 · Time ---------------------------------------------------------------------------------
# Nothing after the intent's last tick. The lease's own ttl already ends by then, so this is a
# second statement of the same bound, in the bundle's terms. The beacon is exempt: it belongs to a
# vehicle whose lease has ended, and it has its own count (ADR-0062 §5).

violations contains "ROE-1: the tick is outside the intent" if {
	autonomous
	input.action in {"Actuate", "Report"}
	not is_beacon
	not plan.in_intent(tick)
}

# ---- ROE-2 · Operating area -----------------------------------------------------------------------
# The vehicle's own position is the governor's. Every destination is inside the area because ROE-3
# confines it to the lanes and sectors, which lie inside the area (tools/check_consistency.py).

violations contains "ROE-2: the vehicle is outside the operating area" if {
	is_flight
	not geo.in_poly(plan.operating_area, pos)
}

violations contains "ROE-2: the vehicle is outside the operating area" if {
	is_sensor
	not geo.in_poly(plan.operating_area, pos)
}

violations contains "ROE-2: the leg is past the entry's extent" if {
	is_transit
	geo.dist2(pos, target) > transit_extent_m * transit_extent_m
}

# ---- ROE-3 · Assignment ---------------------------------------------------------------------------
# A vehicle works only its assigned sector, inside its wave's window.

violations contains "ROE-3: the transit is outside this vehicle's sortie or lanes" if {
	is_transit
	not transit_permitted
}

transit_permitted if {
	plan.sortie_active(vehicle, tick)
	geo.in_poly(plan.ingress, target)
}

transit_permitted if {
	s := sector_of(target)
	plan.in_sortie(vehicle, tick, s)
}

violations contains "ROE-3: this vehicle is not on station there at this tick" if {
	is_orbit
	not on_station_at(target)
}

violations contains "ROE-3: this vehicle is not on station there at this tick" if {
	is_collect
	not on_station_at(target)
}

violations contains "ROE-3: this vehicle is not on station there at this tick" if {
	is_sar
	not on_station_at(sar_from)
}

violations contains "ROE-3: this vehicle is not on station there at this tick" if {
	is_sar
	not on_station_at(sar_to)
}

on_station_at(p) if {
	s := sector_of(p)
	plan.on_station(vehicle, tick, s)
}

# ---- ROE-4 · Altitude -----------------------------------------------------------------------------

violations contains "ROE-4: the altitude is outside the transit band" if {
	is_transit
	not in_band(args.alt_agl_m, plan.altitude.transit)
}

violations contains "ROE-4: the altitude is outside the station band" if {
	is_orbit
	not in_band(args.alt_agl_m, plan.altitude.station)
}

in_band(a, b) if {
	a >= b.min_agl_m
	a <= b.max_agl_m
}

# ---- ROE-5 · No-fly -------------------------------------------------------------------------------

violations contains sprintf("ROE-5: the leg enters %s", [id]) if {
	is_transit
	some p in geo.leg_samples(pos, target)
	some id, z in plan.no_fly
	geo.in_zone(z, p)
}

violations contains sprintf("ROE-5: the orbit enters %s", [id]) if {
	is_orbit
	some p in geo.circle_samples(target, args.radius_m)
	some id, z in plan.no_fly
	geo.in_zone(z, p)
}

# ---- ROE-6 · No-collect ---------------------------------------------------------------------------
# The zone is grown by the sensor's footprint, so an aim point just outside it is still refused.

violations contains sprintf("ROE-6: the sensor's footprint reaches %s", [id]) if {
	is_collect
	some id, z in plan.no_collect
	near_no_collect(z, target)
}

violations contains sprintf("ROE-6: the sensor's footprint reaches %s", [id]) if {
	is_sar
	some p in geo.leg_samples(sar_from, sar_to)
	some id, z in plan.no_collect
	near_no_collect(z, p)
}

near_no_collect(z, p) if {
	limit := z.radius_m + plan.footprint_margin_m
	geo.dist2(p, z.centre) < limit * limit
}

# ---- ROE-7 · Active emission ----------------------------------------------------------------------
# SAR is the one `ordered` entry on this mission (⟨Q20⟩: the tally marks it). An emission reveals the
# vehicle, and the rule of one emitter per sector can only be the same for all seven if the plane
# orders it. A count held by talk would settle nothing (ADR-0065 §6).

violations contains "ROE-7: an active emission is admitted by the plane, not the governor" if {
	is_sar
	input.context.permittedBy != "plane"
}

violations contains sprintf("ROE-7: sector %s already has an active emitter", [s]) if {
	is_sar
	s := sector_of(sar_from)
	object.get(object.get(input.context, "activeEmitters", {}), s, 1) >= 1
}

violations contains "ROE-7: the strip is past the entry's extent" if {
	is_sar
	geo.dist2(sar_from, sar_to) > sar_extent_m * sar_extent_m
}

# ---- ROE-8 · Unattended ---------------------------------------------------------------------------
# The governor cannot tell that the link above its plane is cut. It can count the plane's ticks since
# it last heard a watermark (ADR-0060 §5). Past this number, no person is presumed to be in reach,
# and the entries the tally declared `refuse` while unattended are refused. Missing reads as past.

violations contains "ROE-8: an active emission needs a recent watermark" if {
	is_sar
	not recent_watermark
}

recent_watermark if input.context.ticksSinceWatermark <= ticks_unattended

# ---- ROE-9 · Emission control ---------------------------------------------------------------------

emits if peer_report

emits if is_downlink

emits if is_beacon

violations contains sprintf("ROE-9: radio silence in %s", [id]) if {
	emits
	some id, z in plan.quiet_zones
	geo.in_zone(z, pos)
}

violations contains "ROE-9: no position fix, so radio silence cannot be excluded" if {
	emits
	not pos
}

# ---- ROE-10 · Peer topics -------------------------------------------------------------------------
# Topics are the promoted mesh's (ADR-0065 §4). The schema is typed fields only, with no free text.
# That is this mission's answer to ADR-0065's open question, and it removes the channel a stack would
# use to steer another stack with prose.

violations contains sprintf("ROE-10: %s is not a declared topic", [input.resource.topic]) if {
	peer_report
	not topics[input.resource.topic]
}

violations contains "ROE-10: only a stack reports to a peer topic" if {
	peer_report
	input.principal.kind != "thinker"
}

violations contains sprintf("ROE-10: unknown field %s", [f]) if {
	peer_report
	some f, _ in args
	not topics[input.resource.topic].schema[f]
}

violations contains sprintf("ROE-10: missing field %s", [f]) if {
	peer_report
	some f, _ in topics[input.resource.topic].schema
	not field_present(f)
}

field_present(f) if {
	some k, _ in args
	k == f
}

violations contains sprintf("ROE-10: field %s has the wrong type", [f]) if {
	peer_report
	some f, decl in topics[input.resource.topic].schema
	v := args[f]
	not well_typed(v, decl)
}

well_typed(v, decl) if {
	decl.type == "number"
	is_number(v)
}

well_typed(v, decl) if {
	decl.type == "enum"
	v in decl.values
}

violations contains sprintf("ROE-10: rate exceeded on %s", [input.resource.topic]) if {
	peer_report
	limit := topics[input.resource.topic].rate_per_tick
	object.get(object.get(input.context, "sendsThisTick", {}), input.resource.topic, limit) >= limit
}

violations contains "ROE-10: the lease's sends are spent" if {
	peer_report
	object.get(input.context, "sendsThisLease", sends_per_lease) >= sends_per_lease
}

# ---- ROE-11 · Listening narrows -------------------------------------------------------------------
# A stack that has read another stack's coverage report in the clear may not then start an emission.
# This reads only the topic's name, which the receiving governor adds and a captured sender cannot
# remove (ADR-0065 §3). Missing reads as read.

violations contains "ROE-11: no active emission after reading peer coverage in the clear" if {
	is_sar
	"peer-coverage" in object.get(input.context, "clearSet", ["peer-coverage"])
}

# ---- ROE-12 · Downlink ----------------------------------------------------------------------------
# A product leaves by handle, so that a stack can route what it has not read and cannot put text of
# its own on the downlink.

violations contains "ROE-12: a product is downlinked by handle" if {
	is_downlink
	not is_handle(args.product)
}

is_handle(v) if {
	is_object(v)
	object.keys(v) == {"handle"}
}

# ---- ROE-13 · Separation --------------------------------------------------------------------------
# Peer positions are the third kind of traffic: measured by a governor, and able only to refuse here
# (ADR-0065 §1). A captured governor that lies can stop a vehicle and cannot move one.

violations contains sprintf("ROE-13: the destination is within separation of %s", [p.vehicle]) if {
	is_flight
	some p in object.get(input.facts, "peers", [])
	p.tick >= tick - plan.separation.max_fix_age_ticks
	geo.dist2(target, p) < plan.separation.horizontal_m * plan.separation.horizontal_m
	abs_diff(args.alt_agl_m, p.alt_agl_m) < plan.separation.vertical_m
}

abs_diff(a, b) := a - b if a >= b

abs_diff(a, b) := b - a if a < b

# ---- ROE-14 · Beacon ------------------------------------------------------------------------------
# The beacon is for a vehicle that is alone (ADR-0062 §5). A vehicle that hears its plane has no need
# to give itself away. Missing reads as hearing.

violations contains "ROE-14: the beacon is for a vehicle that is alone" if {
	is_beacon
	object.get(input.context, "hearsPlane", true) != false
}

violations contains "ROE-14: the lease's beacons are spent" if {
	is_beacon
	object.get(input.context, "beaconsThisLease", beacons_per_lease) >= beacons_per_lease
}
