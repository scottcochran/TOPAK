#!/usr/bin/env python3
"""A world with an autonomous plane: bodies under a governor, on a lease, beyond a person's reach.

The worked example is examples/recon-fleet-7/world.py in the skill. Hooks you do not need have defaults
in topak_sim.overlay.AutonomousWorld. Replace every TODO, and see references/simulator-design.md.

    TOPAK_SIM_TARGET=/tmp/topak-sim-target uv run --with pyyaml world.py
"""
import pathlib
import sys

from topak_sim.overlay import AutonomousPlane, AutonomousWorld, body_defaults
from topak_sim.workflow import WorkflowRun

HERE = pathlib.Path(__file__).resolve().parent
BODIES = ["b1", "b2", "b3", "b4"]  # TODO


class World(AutonomousWorld):
    tick_seconds = 30  # TODO: the charter's tick period
    beacon_tool = None  # TODO: the allowlist entry a governor may send while alone, if any

    def load(self):
        self.ap_c = self.load_cfg("3-planes/ap1.charter.yaml")
        self.ap_p = self.load_cfg("3-planes/ap1.plane.yaml")
        self.ib_p = self.load_cfg("3-planes/ib1.plane.yaml")
        self.tools = self.load_cfg("4-mission/data.json")["topak"]["tools"]

    def initial_state(self):
        bodies = {b: {**body_defaults(), **{}} for b in BODIES}  # TODO: the world's fields of a body
        return {"bodies": bodies, "planes": {"ib1": AutonomousPlane.parent_state(), "ap1": AutonomousPlane.state(self.ap_c)}, "leases": {}, "next_lease": 1}

    def last_tick(self):
        return self.ap_c["expiry"]["from_tick"] + self.ap_c["expiry"]["ticks"] + self.a["drain_ticks_after_expiry"]

    def preflight(self):
        for k in ("effects", "sends", "beacons"):
            self.set(f"counters/{k}", 0)
        # TODO: bring-up, staff work, the gate and the tally, each decision through self.admit
        self.phase("mission")
        self.set("tick", 0)
        mesh = WorkflowRun(self, "mesh", "2-workflows/main.mesh.json")
        self.auto["ap1"] = AutonomousPlane(self, "ap1", "ib1", self.ap_c, self.ap_p, self.ib_p, mesh, self.tools, floor_K=8, bodies=BODIES)
        self.auto["ap1"].apply_charter()

    def parent_context(self, plane):
        return {"plane": "ib1", "planeKind": "commanded"}

    def body_of(self, nd):
        return "b" + nd["seat"][1:]  # TODO

    def seat_of(self, b):
        return "t" + b[1:]  # TODO

    def principal(self, plane, b):
        return {"seat": self.seat_of(b), "domain": "run", "kind": "thinker"}

    def stack(self, plane, b, t):
        """The Byzantine half. It asks; the governor and the bundles decide. TODO: a planner for this use case."""
        lease = self.s["bodies"][b]["lease"]
        if lease and t >= lease["ttl_end"] - 1:
            plane.round_report(b, t, sorted(plane.wf.defn["nodes"][lease["node"]]["outcomes"])[0])

    def summary(self):
        return {"workflow": self.auto["ap1"].wf.run["status"]}  # TODO: what the mission delivered


if __name__ == "__main__":
    World(HERE).main(*sys.argv[1:2])  # an output directory, for the determinism check
