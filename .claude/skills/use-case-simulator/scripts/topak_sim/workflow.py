"""A promoted DAG or mesh, driven through the reference's own workflow Run.

The semantics live in `topak_core::workflow`: guards, routing taint, joins, skips, the budget, completion
and failure. This wrapper only says when a round is granted, ends, is covered or is routed, and copies
the run into the simulation's state.
"""
from .trace import canonical

# Fields the overlay adds to a workflow text, which the reference's closed schema refuses.
OVERLAY_NODE_FIELDS = ("lease", "observer")
OVERLAY_TOP_FIELDS = ("topics",)


def status_of(x):
    return x["status"] if isinstance(x, dict) else x


class WorkflowRun:
    WAIT = object()  # from a `route` callback: nobody has decided yet, and the round still holds the event

    def __init__(self, sim, name, rel, seats=None):
        self.sim, self.name, self.rel, self.path = sim, name, rel, f"workflows/{name}"
        self.defn = sim.load_cfg(rel)
        stripped = {k: v for k, v in self.defn.items() if k not in OVERLAY_TOP_FIELDS}
        stripped["nodes"] = {n: {k: v for k, v in nd.items() if k not in OVERLAY_NODE_FIELDS} for n, nd in self.defn["nodes"].items()}
        if seats is None:
            seats = {nd["seat"]: {"kind": "thinker", "domain": "run", "rung": nd["confinement"]["rung"]} for nd in self.defn["nodes"].values()}
            if self.defn.get("orchestrator"):
                o = self.defn["orchestrator"]
                seats[o["seat"]] = {"kind": "orchestrator", "domain": "run", "rung": o["confinement"]["rung"]}
        r = sim.eng.request({"op": "wf_load", "run": name, "text": canonical(stripped), "seats": seats})
        if "err" in r:
            raise SystemExit(f"{rel}: the reference's parser refuses it: {r['err']}")
        self.load_check = r["check"]
        sim.set(self.path, r["run"])
        sim.emit("workflow_loaded", workflow=name, file=rel, load_check=self.load_check, overlay_fields_stripped=[f for f in OVERLAY_NODE_FIELDS + OVERLAY_TOP_FIELDS if f in canonical(self.defn)])

    @property
    def run(self):
        return self.sim.s["workflows"][self.name]

    def status(self):
        return status_of(self.run["status"])

    def act(self, i):
        return self.run["acts"][i]

    def act_status(self, i):
        return status_of(self.act(i)["status"])

    def node_of(self, i):
        return self.defn["nodes"][self.act(i)["node"]]

    def ready(self):
        return [i for i, a in enumerate(self.run["acts"]) if status_of(a["status"]) == "ready"]

    def running_node(self, node):
        return any(a["node"] == node and status_of(a["status"]) == "running" for a in self.run["acts"])

    def open_events(self):
        return [int(k) for k, v in sorted(self.run["events"].items(), key=lambda kv: int(kv[0])) if status_of_event(v) == "open"]

    def served_events(self):
        return [int(k) for k, v in sorted(self.run["events"].items(), key=lambda kv: int(kv[0])) if status_of_event(v) == "served"]

    def route_facts(self, event, edge):
        """The keyword arguments lift.run_action needs for a Route out of this decision event."""
        node = f"{self.name}/{self.act(event)['node']}"
        return {"edge": edge, "edge_uid": f"{self.name}/{edge}", "edge_source": node, "edge_chosen": self.defn["edges"][edge]["kind"] == "chosen", "decision_point": node}

    def enabled(self, event):
        """The chosen edges out of a decision event: edge id to None if enabled, or why it is not."""
        return self.sim.eng.request({"op": "wf_enabled", "run": self.name, "event": event})["edges"]

    def _op(self, op, **kw):
        r = self.sim.eng.request({"op": op, "run": self.name, **kw})
        if "err" in r:
            return r
        self.sim.sync(self.path, r["run"])
        return r

    def grant(self, act, fence=None):
        """Charges the budget. A reply with `refused` means no grant, and a mesh has failed."""
        return self._op("wf_grant", act=act, fence=fence)

    def grant_decision(self, event, fence=None):
        return self._op("wf_grant_decision", event=event, fence=fence)

    def end(self, act, end="outcome", outcome=None, label=(), actuates=0):
        return self._op("wf_end", act=act, end=end, outcome=outcome, label=sorted(label), actuates=actuates)

    def cover(self, act):
        return self._op("wf_cover", act=act)

    def finding(self, act):
        return self._op("wf_finding", act=act)

    def fail(self, act, why):
        return self._op("wf_fail", act=act, why=why)

    def route(self, event, edge):
        return self._op("wf_route", event=event, edge=edge)

    def lapse(self, event, why):
        return self._op("wf_lapse", event=event, why=why)

    def fence(self):
        return self._op("wf_fence")

    def step(self, work, route, observed=lambda act: True):
        """One pass of a workflow on a commanded plane. Returns whether anything moved.

        work(act, node)          performs a ready node's round and returns wf.end's keyword arguments
        route(event, enabled)    decides a decision event: an enabled edge's id, admitted by the world; None to
                                 let the round lapse, which fails the event; or WorkflowRun.WAIT to decide later
        observed(act)            whether the node's Observer has read to the seal
        """
        moved = False
        for i in self.ready():
            node = self.act(i)["node"]
            r = self.grant(i)
            if "refused" in r:
                self.sim.emit("wf_refused", workflow=self.name, act=i, node=node, why=r["refused"])
                return True
            self.sim.emit("wf_grant", workflow=self.name, act=i, node=node, seat=self.defn["nodes"][node]["seat"])
            res = work(i, node)
            r = self.end(i, **res)
            self.sim.emit("wf_end", workflow=self.name, act=i, node=node, **{k: v for k, v in res.items() if k != "label"}, label=sorted(res.get("label", ())))
            moved = True
        for i, a in enumerate(self.run["acts"]):
            if status_of(a["status"]) == "ended" and not a["covered"] and observed(i):
                r = self.cover(i)
                self.sim.emit("wf_covered", workflow=self.name, act=i, node=a["node"], fired=r.get("fired", []))
                moved = True
        # One orchestrator round at a time, as the reference grants them (workflow_ready).
        if not self.served_events() and self.open_events():
            self.grant_decision(self.open_events()[0])
            moved = True
        for ev in self.served_events():
            enabled = self.enabled(ev)
            edge = route(ev, enabled)
            if edge is self.WAIT:
                continue
            if edge is None:
                self.lapse(ev, "the orchestrator's round ended with no route")
                self.sim.emit("wf_lapsed", workflow=self.name, event=ev)
            else:
                r = self.route(ev, edge)
                self.sim.emit("wf_routed", workflow=self.name, event=ev, edge=edge, result=r.get("err", "applied"))
            moved = True
        return moved

    def drive(self, work, route, observed=lambda act: True, limit=100000):
        """Step until the run stops moving, for a workflow that completes inside one simulated instant."""
        for _ in range(limit):
            if not self.step(work, route, observed):
                break
        self.sim.emit("wf_status", workflow=self.name, status=self.status(), detail=self.run["status"])


def status_of_event(v):
    return v["state"] if isinstance(v, dict) else v
