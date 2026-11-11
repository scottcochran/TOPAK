#!/usr/bin/env python3
"""A world on a commanded plane: agents and people under a promoted workflow, no bodies.

Replace every TODO. See references/simulator-design.md. Run with:

    TOPAK_SIM_TARGET=/tmp/topak-sim-target uv run --with pyyaml world.py
"""
import pathlib
import sys

from topak_sim import lift
from topak_sim.core import Core
from topak_sim.workflow import WorkflowRun

HERE = pathlib.Path(__file__).resolve().parent
PLANE = "plane1"


class World(Core):
    tick_seconds = None  # TODO: seconds a tick stands for, if a tick is a span of time
    inside_targets = ()  # TODO: channel targets inside the deployment. Every other channel is outward

    def load(self):
        # TODO: read the configuration. Read constants out of the Rego with self.rego_value, not by retyping them.
        self.tools = {t["name"]: t for t in self.load_cfg("1-bundles/standing/data.json")["topak"]["tools"].values()}

    def initial_state(self):
        return {"world": {}}  # TODO: everything the mission's outcome depends on

    def last_tick(self):
        return 100  # TODO

    def preflight(self):
        self.phase("run")
        self.set("tick", 0)
        self.wf = WorkflowRun(self, "main", "2-workflows/main.dag.json")

    def actuate(self, seat, kind, node, tool, inputs, why=None, handles=None, clear_set=(), round_=1):
        """One Actuate through the real admit path: the linked floor, then the bundle chain."""
        t = self.tools.get(tool)
        facts = lift.label_facts(t, inputs, handles, self.inside_targets)  # without these, floor rules R5 to R7 can never fire
        frozen = lift.run_action(seat, kind, "Actuate", ["Actuate", "Consult", "Report"], tool=tool, digest=t["digest"] if t else "0" * 64, allowlisted=t is not None, inputs=inputs, handles=handles, clear_set=clear_set, round_=round_, **facts)
        return self.admit(f"seat:{seat}", self.chains[PLANE], frozen["bundle_input"], tool, why, floor=frozen["floor"])

    def work(self, act, node):
        """A node's round: the requests its stack makes. Returns how the round ended."""
        nd = self.wf.defn["nodes"][node]
        # TODO: issue this node's requests with self.actuate, including ones that should be refused
        if node == "work":
            self.actuate(nd["seat"], "thinker", node, "example.lookup", {"ref": "item-1"})
            self.actuate(nd["seat"], "thinker", node, "not.on.the.list", {}, why="a tool the allowlist does not hold")
        return {"outcome": "ok" if "ok" in nd["outcomes"] else sorted(nd["outcomes"])[0]}

    def route(self, event, enabled):
        """A decision point. Admit the Route, and return the edge. None lets the round lapse, and
        self.wf.WAIT leaves the event held for a later tick, for a person who has not answered yet."""
        choices = sorted(e for e, why in enabled.items() if why is None)
        if not choices:
            return None
        edge = choices[0]  # TODO: who decides, and on what
        o = self.wf.defn["orchestrator"]
        frozen = lift.run_action(o["seat"], "orchestrator", "Route", o["alphabet"], **self.wf.route_facts(event, edge))
        return edge if self.admit(f"seat:{o['seat']}", self.chains[PLANE], frozen["bundle_input"], f"Route {edge}", floor=frozen["floor"]) else None

    def step(self, t):
        # TODO: inject the scenario's events for tick t
        if self.wf.status() == "running":
            self.wf.step(self.work, self.route)
        # TODO: self.invariant(condition, "the record this property comes from"), and self.measure(...)
        return {}

    def summary(self):
        return {"workflow": self.wf.run["status"]}  # TODO: what the use case delivered


if __name__ == "__main__":
    World(HERE).main(*sys.argv[1:2])  # an output directory, for the determinism check
