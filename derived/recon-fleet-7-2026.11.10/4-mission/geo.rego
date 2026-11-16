# Plane geometry for the mission bundle: planar metres in the mission's local east-north frame.
#
# Pure functions, with no reference to the mission. Only arithmetic and comparison, so the module
# compiles to OPA Wasm with no host builtin. A point is {"e": metres, "n": metres}. A polygon is a list
# of [e, n] pairs. Distances stay squared, so no square root is needed.
package topak.mission.geo

dist2(a, b) := ((a.e - b.e) * (a.e - b.e)) + ((a.n - b.n) * (a.n - b.n))

# Ray casting: an edge counts if a ray east from `p` crosses it. The first line guarantees the edge
# is not horizontal, so the division cannot be by zero.
crosses(poly, p, i) if {
	a := poly[i]
	b := poly[(i + 1) % count(poly)]
	(a[1] > p.n) != (b[1] > p.n)
	p.e < (((b[0] - a[0]) * (p.n - a[1])) / (b[1] - a[1])) + a[0]
}

in_poly(poly, p) if {
	hits := {i | some i, _ in poly; crosses(poly, p, i)}
	count(hits) % 2 == 1
}

# A zone is a circle or a polygon.
in_zone(z, p) if {
	z.shape == "circle"
	dist2(p, z.centre) < z.radius_m * z.radius_m
}

in_zone(z, p) if {
	z.shape == "poly"
	in_poly(z.points, p)
}

# Fixed fractions along a leg. Thirty-two intervals over a transit's 40 km extent is 1.25 km between
# samples, which is under the narrowest zone in the plan (a 3 km circle).
fractions := [
	0, 0.03125, 0.0625, 0.09375, 0.125, 0.15625, 0.1875, 0.21875,
	0.25, 0.28125, 0.3125, 0.34375, 0.375, 0.40625, 0.4375, 0.46875,
	0.5, 0.53125, 0.5625, 0.59375, 0.625, 0.65625, 0.6875, 0.71875,
	0.75, 0.78125, 0.8125, 0.84375, 0.875, 0.90625, 0.9375, 0.96875,
	1,
]

along(a, b, f) := {"e": a.e + ((b.e - a.e) * f), "n": a.n + ((b.n - a.n) * f)}

leg_samples(a, b) := [along(a, b, f) | some f in fractions]

# Eight points on a circle, for testing an orbit against a zone of either shape.
circle_samples(c, r) := [
	{"e": c.e + r, "n": c.n},
	{"e": c.e - r, "n": c.n},
	{"e": c.e, "n": c.n + r},
	{"e": c.e, "n": c.n - r},
	{"e": c.e + (r * 0.7071), "n": c.n + (r * 0.7071)},
	{"e": c.e + (r * 0.7071), "n": c.n - (r * 0.7071)},
	{"e": c.e - (r * 0.7071), "n": c.n + (r * 0.7071)},
	{"e": c.e - (r * 0.7071), "n": c.n - (r * 0.7071)},
	c,
]
