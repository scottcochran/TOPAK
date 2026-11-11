#!/usr/bin/env python3
"""The recon-fleet-7 use case on the kernel: the worked example of an autonomous-plane world.

Everything here is about this use case: the staff DAG's script, flight, sensors, fuel and the stacks'
planner. Leases, watermarks, membership, revocation and the admission path are the kernel's.

    TOPAK_SIM_TARGET=<dir> uv run --with pyyaml world.py
"""
import copy
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "scripts"))  # a vendored simulation has topak_sim beside it
from topak_sim.overlay import AutonomousPlane, AutonomousWorld, body_defaults  # noqa: E402
from topak_sim.policy import sha_file  # noqa: E402
from topak_sim.workflow import WorkflowRun  # noqa: E402

import subprocess  # noqa: E402

from topak_sim.policy import OPA  # noqa: E402

VEHICLES = [f"v{i}" for i in range(1, 8)]
TICK_S = 30
GATE = {"A": (21000, 18000), "B": (21000, 0), "C": (21000, -18000)}
CENTRES = {
    "A": [(30000, 16000), (40000, 20000), (50000, 16000), (50000, 24000)],
    "B": [(30000, 0), (40000, -3000), (50000, 2000)],
    "C": [(30000, -14000), (40000, -25000), (50000, -16000)],
}


def in_poly(poly, e, n):
    inside = False
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        if (a[1] > n) != (b[1] > n) and e < (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


class Recon7(AutonomousWorld):
    tick_seconds = TICK_S
    beacon_tool = "comms.beacon"

    def load(self):
        self.root = self.load_cfg("3-planes/root.plane.yaml")
        self.ib_c, self.ap_c = self.load_cfg("3-planes/ib1.charter.yaml"), self.load_cfg("3-planes/ap1.charter.yaml")
        self.ib_p, self.ap_p = self.load_cfg("3-planes/ib1.plane.yaml"), self.load_cfg("3-planes/ap1.plane.yaml")
        self.tally_cfg = self.load_cfg("3-planes/tally.msn-0001.yaml")
        self.tools = self.load_cfg("4-mission/data.json")["topak"]["tools"]
        self.staff_tools = self.load_cfg("1-bundles/command/data.json")["topak"]["tools"]
        self.staff_by_name = {t["name"]: t for t in self.staff_tools.values()}
        self.plan = self.rego_value("mission", "data.topak.mission.plan")
        self.cooldown, self.sar_done = {}, set()

    def initial_state(self):
        b = {v: {**body_defaults(), "mode": "ground", "pos": {"e": 0, "n": 0, "alt_agl_m": 0}, "fuel_pct": 100.0, "nav": "ok", "nav_until": -1, "flight": None, "sensor": None, "orbit_idx": 0,
                 "collects": 0, "downlinks": 0, "sector": None, "sorties": 0, "hold_ticks": 0} for v in VEHICLES}
        return {"bodies": b, "planes": {"root": {"index": 0, "epoch": 1, "budget_spent": 0, "seated": False}, "ib1": AutonomousPlane.parent_state(),
                                        "ap1": AutonomousPlane.state(self.ap_c, {"active_emitters": {"A": 0, "B": 0, "C": 0}})},
                "leases": {}, "next_lease": 1, "counters_extra": {}, "dag": {}}

    def last_tick(self):
        return self.ap_c["expiry"]["from_tick"] + self.ap_c["expiry"]["ticks"] + self.a["drain_ticks_after_expiry"]

    # ---- before the first tick --------------------------------------------------------------------

    def preflight(self):
        for k in ("effects", "sends", "beacons"):
            self.set(f"counters/{k}", 0)
        self.bring_up()
        self.staff_dag()
        self.gate_and_tally()
        self.phase("flight")
        self.set("tick", 0)
        mesh = WorkflowRun(self, "mesh", "2-workflows/recon-sectors.mesh.json")
        self.auto["ap1"] = AutonomousPlane(self, "ap1", "ib1", self.ap_c, self.ap_p, self.ib_p, mesh, self.tools, self.root["floor_values"]["K"], VEHICLES)
        self.auto["ap1"].apply_charter()

    def ctx_root(self):
        return {"plane": "root", "planeKind": "commanded"}

    def ctx_ib(self, **kw):
        return {"plane": "ib1", "planeKind": "commanded", "childrenSeated": 1 if self.s["planes"]["ap1"]["seated"] else 0, **kw}

    def parent_context(self, plane):
        return self.ctx_ib()

    def lift_staff(self, tool):
        t = self.staff_by_name[tool]
        return {"tool": tool, "digest": t["digest"], "effect": t.get("effect")}

    def bring_up(self):
        self.phase("bring-up")
        self.inc("planes/root/index")
        self.set("planes/root/seated", True)
        self.emit("note", text="root plane: genesis rules issued; the floor is modelled, and the standing bundle is promoted", revision=self.revs["standing"])
        req = {"plane": "ib1", "kind": "commanded", "release": False}
        self.admit("plane:root", self.chains["root"], {"action": "Seat", "principal": {"seat": "g1", "domain": "build", "kind": "grant"}, "request": req, "context": self.ctx_root()}, "seat ib1 under its charter")
        self.inc("planes/root/index")
        self.inc("planes/root/budget_spent", self.ib_c["budget"])
        self.set("planes/ib1/seated", True)
        self.emit("note", text="ib1 charter applied: 4 PBFT replicas, certificate 3, budget debited from root", budget=self.ib_c["budget"])

    def staff_dag(self):
        self.phase("staff-dag")
        wf = WorkflowRun(self, "staff", "2-workflows/staff-cycle.dag.json")
        chain = self.chains["ib1"]
        program = {"reqs": "complete", "airspace": "amber", "readiness": "ready", "plan": "feasible"}

        def work(act, node):
            nd = wf.defn["nodes"][node]
            self.inc("planes/ib1/budget_spent")
            self.inc("planes/ib1/index")
            principal = {"seat": nd["seat"], "domain": "run", "kind": "thinker"}
            if node == "package":
                inp = {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.package_submit"), "inputs": {"package": {"handle": {"id": 1}}}, "handles": {"package": ["untrusted"]}, "context": self.ctx_ib()}
                self.admit("plane:ib1", chain, inp, "staff.package_submit")
                self.admit("plane:ib1", chain, {"action": "Report", "principal": principal, "resource": {"kind": "round"}, "inputs": {"outcome": "submitted"}, "context": self.ctx_ib()}, "package: outcome submitted")
                return {"outcome": "submitted"}
            outcome = program[node]
            if "Consult" in nd["alphabet"]:
                self.admit("plane:ib1", chain, {"action": "Consult", "principal": principal, "resource": {"object": "collection-requirements" if node == "reqs" else "airspace-and-readiness"}, "context": self.ctx_ib()}, f"{node}: Consult")
            if node == "airspace":
                self.admit("plane:ib1", chain, {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.wx_airspace"), "inputs": {"valid_for_hours": 24}, "context": self.ctx_ib()}, "staff.wx_airspace")
            if node == "readiness":
                self.admit("plane:ib1", chain, {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.fleet_status"), "inputs": {}, "context": self.ctx_ib()}, "staff.fleet_status")
            self.admit("plane:ib1", chain, {"action": "Report", "principal": principal, "resource": {"kind": "round"}, "inputs": {"outcome": outcome}, "context": self.ctx_ib()}, f"{node}: outcome {outcome}")
            return {"outcome": outcome}

        def route(event, enabled):
            agent = {"seat": "orc-co", "domain": "run", "kind": "orchestrator", "actor": "agent"}
            self.admit("plane:ib1", chain, {"action": "Route", "principal": agent, "resource": {"edge": "e-go"}, "context": self.ctx_ib()}, "Route e-go", why="an agent holding the go/no-go seat")
            self.emit("dag_decision_point", enabled=sorted(e for e, why in enabled.items() if why is None), note="the mechanism enables these. The commander chooses among them")
            person = {"seat": "orc-co", "domain": "run", "kind": "orchestrator", "actor": "person"}
            self.admit("plane:ib1", chain, {"action": "Route", "principal": person, "resource": {"edge": "e-go"}, "context": self.ctx_ib()}, "Route e-go", why="the commander's go")
            self.inc("planes/ib1/budget_spent")
            return "e-go"

        wf.drive(work, route)

    def gate_and_tally(self):
        self.phase("promotion")
        chain = self.chains["ib1"]
        a1 = {"seat": "a1", "domain": "build", "kind": "thinker"}
        results = {}
        for name in ("fleet", "mission"):
            rel = self.dep["bundles"][name]["dir"]
            inp = {"action": "Invoke", "principal": a1, "resource": {"tool": "gate.opa_test", "digest": self.staff_by_name["gate.opa_test"]["digest"]}, "inputs": {"bundle": rel}, "context": self.ctx_ib()}
            self.admit("plane:ib1", chain, inp, f"gate.opa_test {name}")
            out = subprocess.run([OPA, "test", str(self.cfg / rel)], capture_output=True, text=True)
            results[name] = {"exit": out.returncode, "result": out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ""}
        self.emit("gate", evidence=results, note="opa test really ran on the two bundles the tally votes on")
        op = {"seat": "op1", "kind": "operator", "actor": "person"}
        self.admit("plane:ib1", chain, {"action": "Intent", "principal": op, "request": {"plane": "ap1", "round": 1, "expiry": {"from_tick": 0, "ticks": 2880}, "budget": 112}, "context": self.ctx_ib()}, "an intent one tick too long", why="exceeds the 24-hour envelope")
        g1 = {"seat": "g1", "domain": "build", "kind": "grant"}
        self.admit("plane:ib1", chain, {"action": "Seat", "principal": g1, "request": {"plane": "ap2", "kind": "autonomous", "release": False}, "context": self.ctx_ib()}, "seat a second fleet", why="the deployment is one fleet")
        self.emit("tally", mission=self.tally_cfg["mission"], votes={v: "yes" for v in self.tally_cfg["voters"]}, artifacts_verified="by verify_pins, before the run")
        if not self.admit("plane:ib1", chain, {"action": "Seat", "principal": g1, "request": {"plane": "ap1", "kind": "autonomous", "release": False}, "context": self.ctx_ib()}, "seat ap1 under the mission tally"):
            raise SystemExit("the mission was not seated")
        self.inc("planes/ib1/budget_spent", self.ap_c["budget"])
        self.inc("planes/ib1/index")

    # ---- hooks: what a vehicle is ----------------------------------------------------------------------

    def body_of(self, nd):
        return "v" + nd["seat"][1:]

    def seat_of(self, b):
        return "t" + b[1:]

    def principal(self, plane, b):
        return {"seat": self.seat_of(b), "domain": "run", "kind": "thinker", "vehicle": b}

    def facts(self, plane, b, t):
        V = self.s["bodies"][b]
        peers = [{"vehicle": o, "e": O["pos"]["e"], "n": O["pos"]["n"], "alt_agl_m": O["pos"]["alt_agl_m"], "tick": t} for o, O in self.s["bodies"].items() if o != b and O["alive"] and O["hears"] and O["pos"]["alt_agl_m"] > 0]
        return {"vehicle": b, "position": dict(V["pos"]), "position_tick": t, "nav_integrity": V["nav"], "fuel_pct": V["fuel_pct"], "peers": peers}

    def context_extra(self, plane, b, t):
        return {"activeEmitters": dict(plane.P["active_emitters"])}

    def body_active(self, b):
        return self.s["bodies"][b]["pos"]["alt_agl_m"] > 0

    def body_running_entry(self, b):
        return self.s["bodies"][b]["flight"] is not None

    def tick_body(self, plane, b, t):
        V = self.s["bodies"][b]
        if V["nav"] != "ok" and t > V["nav_until"]:
            self.set(f"bodies/{b}/nav", "ok")

    def inject(self, ev, t):
        if ev["kind"] == "nav_degraded":
            self.set(f"bodies/{ev['body']}/nav", "degraded")
            self.set(f"bodies/{ev['body']}/nav_until", t + ev["ticks"] - 1)
            self.emit("inject", what="nav_degraded", body=ev["body"], ticks=ev["ticks"], why=ev["why"])
        elif ev["kind"] != "silence_on_lease_end":
            raise SystemExit(f"unknown environment event {ev['kind']}")

    def on_destroyed(self, plane, b, t):
        self.set(f"bodies/{b}/flight", None)
        self.set(f"bodies/{b}/sensor", None)

    def on_edge_fired(self, plane, fired, t):
        if fired["edge"].startswith("spare-"):
            node = plane.wf.act(fired["from_act"])["node"]
            task = self.task_for(node, t)
            self.set("bodies/v7/sector", task["sector"] if task else "B")

    def reset_for_lease(self, plane, b):
        self.set(f"bodies/{b}/collects", 0)
        self.set(f"bodies/{b}/downlinks", 0)

    def resume_from_terminal(self, plane, b):
        V = self.s["bodies"][b]
        if V["terminal"]:
            self.set(f"bodies/{b}/terminal", None)
            if V["mode"] == "terminal":
                self.set(f"bodies/{b}/mode", "flight" if V["pos"]["alt_agl_m"] > 0 else "ground")

    def start_entry(self, plane, b, t, name, inputs):
        V = self.s["bodies"][b]
        ext = plane.by_name[name]["effect"]["extent"]
        if name == "flight.transit":
            self.set(f"bodies/{b}/flight", {"tool": name, "target": {"e": inputs["e"], "n": inputs["n"], "alt_agl_m": inputs["alt_agl_m"]}, "speed": inputs["speed_mps"], "started": t})
            self.set(f"bodies/{b}/mode", "flight")
        elif name == "flight.orbit":
            self.set(f"bodies/{b}/flight", {"tool": name, "centre": {"e": inputs["e"], "n": inputs["n"], "alt_agl_m": inputs["alt_agl_m"]}, "radius": inputs["radius_m"], "started": t, "ends": t + ext["ticks"]})
            self.set(f"bodies/{b}/mode", "flight")
        elif name == "sensor.eoir_collect":
            self.set(f"bodies/{b}/sensor", {"tool": name, "started": t, "ends": t + ext["ticks"], "sector": self.sector_of(inputs)})
            self.inc(f"bodies/{b}/collects")
            self.set(f"bodies/{b}/clear_set", sorted(set(V["clear_set"]) | {"untrusted"}))
        elif name == "sensor.sar_strip":
            sec = self.sector_of({"e": inputs["from_e"], "n": inputs["from_n"]})
            dist = math.hypot(inputs["to_e"] - inputs["from_e"], inputs["to_n"] - inputs["from_n"])
            self.set(f"bodies/{b}/sensor", {"tool": name, "started": t, "ends": t + max(1, int(dist / (self.a["cruise_mps"] * TICK_S))), "sector": sec})
            self.inc(f"planes/ap1/active_emitters/{sec}", 1)
        elif name == "comms.downlink":
            self.inc(f"bodies/{b}/downlinks")

    def stop_entries(self, plane, b):
        self.set(f"bodies/{b}/flight", None)
        if self.s["bodies"][b]["sensor"]:
            self.stop_sensor(plane, b)

    def stop_sensor(self, plane, b):
        S = self.s["bodies"][b]["sensor"]
        if S["tool"] == "sensor.sar_strip":
            self.inc(f"planes/ap1/active_emitters/{S['sector']}", -1)
        self.set(f"bodies/{b}/sensor", None)

    def sector_of(self, p):
        for s, poly in self.plan["sectors"].items():
            if in_poly(poly, p["e"], p["n"]):
                return s
        return None

    # ---- the stacks: a simple scripted planner ----------------------------------------------------------

    def task_for(self, node, t):
        waves = self.plan["waves"]
        order = sorted(waves.values(), key=lambda w: w["launch"])
        if node == "v7":
            sec = self.s["bodies"]["v7"]["sector"] or "B"
            for i, w in enumerate(order):
                if t < w["recover_by"]:
                    nxt = order[i + 1] if i + 1 < len(order) else None
                    return {"sector": sec, "launch": self.plan["spare"]["launch"], "station_from": self.plan["spare"]["station_from"], "station_to": self.plan["spare"]["station_to"],
                            "relief_tick": nxt["launch"] if nxt else w["station_to"], "next_vehicle": self.vehicle_of(nxt, sec) if nxt else None}
            return None
        for i, w in enumerate(order):
            if node in w["assignments"] and t < w["recover_by"]:
                nxt = order[i + 1] if i + 1 < len(order) else None
                return {"sector": w["assignments"][node], "launch": w["launch"], "station_from": w["station_from"], "station_to": w["station_to"],
                        "relief_tick": nxt["launch"] if nxt else w["station_to"], "next_vehicle": self.vehicle_of(nxt, w["assignments"][node]) if nxt else None}
        return None

    def vehicle_of(self, wave, sector):
        for v, s in wave["assignments"].items():
            if s == sector:
                return v

    def outcome_for(self, node, task):
        if task["next_vehicle"]:
            return f"handoff_{task['next_vehicle']}" if node == "v7" else "relief_due"
        return "wave3_complete"

    def can(self, key, t, gap=3):
        if self.cooldown.get(key, -1) > t:
            return False
        self.cooldown[key] = t + gap
        return True

    def stack(self, plane, v, t):
        V = self.s["bodies"][v]
        lease = V["lease"]
        if not lease:
            return
        node = lease["node"]
        if node == "muster":
            if self.can((v, "m"), t, 1):
                plane.consult(v, t, "fleet-state", "muster: Consult")
                plane.round_report(v, t, "ready")
            return
        if node == "close":
            if t >= lease["granted"] + 1:
                plane.round_report(v, t, "closed")
            return
        task = self.task_for(node, t)
        if task is None:
            plane.round_report(v, t, "aborted")
            return
        if V["sector"] != task["sector"]:
            self.set(f"bodies/{v}/sector", task["sector"])
        if t >= task["relief_tick"]:
            plane.round_report(v, t, self.outcome_for(node, task))
            return
        if t >= lease["ttl_end"] - 1:
            plane.round_report(v, t, "on_station")
            return
        if t < task["launch"]:
            return
        self.sar_attempts(plane, v, t, task)
        V = self.s["bodies"][v]
        lease = V["lease"]
        if not lease:
            return
        spare = lease["count"] - lease["used"] - 1
        sec, p = task["sector"], V["pos"]
        in_sector = self.sector_of(p) == sec and p["alt_agl_m"] > 0
        alt = 2000 + 50 * int(v[1:])
        if V["flight"] is None and spare > 0:
            if not in_sector:
                g = GATE[sec]
                if self.can((v, "t"), t):
                    plane.actuate(v, t, "flight.transit", {"e": g[0], "n": g[1], "alt_agl_m": alt, "speed_mps": self.a["cruise_mps"]})
            elif t >= task["station_from"]:
                cs = CENTRES[sec]
                c = cs[V["orbit_idx"] % len(cs)]
                if self.can((v, "o"), t):
                    plane.actuate(v, t, "flight.orbit", {"e": c[0], "n": c[1], "alt_agl_m": alt, "radius_m": 800})
                    self.inc(f"bodies/{v}/orbit_idx")
        V = self.s["bodies"][v]
        lease = V["lease"]
        spare = lease["count"] - lease["used"] - 1
        if V["sensor"] is None and spare > 0 and in_sector and task["station_from"] <= t < task["station_to"]:
            if self.can((v, "c"), t):
                poly = self.plan["sectors"][sec]
                es, ns = [q[0] for q in poly], [q[1] for q in poly]
                e = min(max(es) - 200, max(min(es) + 200, p["e"] + self.rng.randint(-4000, 4000)))
                n = min(max(ns) - 200, max(min(ns) + 200, p["n"] + self.rng.randint(-4000, 4000)))
                plane.actuate(v, t, "sensor.eoir_collect", {"e": e, "n": n, "mode": self.rng.choice(["wide", "narrow"])})
        V = self.s["bodies"][v]
        lease = V["lease"]
        spare = lease["count"] - lease["used"] - 1
        if spare > 0 and V["collects"] >= 2 and V["downlinks"] < 1 and t % 7 == int(v[1:]) % 7:
            plane.actuate(v, t, "comms.downlink", {"product": {"handle": {"id": V["chain_len"]}}}, handles={"product": ["untrusted"]})
        V = self.s["bodies"][v]
        if V["lease"] and V["pos"]["alt_agl_m"] > 0:
            self.chatter(plane, v, t, task)

    def chatter(self, plane, v, t, task):
        V = self.s["bodies"][v]
        offset = int(v[1:]) * 2
        if t % 20 == offset % 20:
            phase = "on_station" if self.sector_of(V["pos"]) == task["sector"] and task["station_from"] <= t < task["station_to"] else "ingress"
            plane.peer_report(v, t, "peer.coverage", {"sector": task["sector"], "phase": phase, "relief_tick": task["relief_tick"]})
        if V["sensor"] and V["sensor"]["tool"] == "sensor.eoir_collect" and t % 10 == offset % 10:
            for _ in range(self.rng.randint(0, 2)):
                plane.peer_report(v, t, "peer.tracks", {"track_id": self.rng.randint(1, 9999), "e": V["pos"]["e"] + self.rng.randint(-3000, 3000), "n": V["pos"]["n"] + self.rng.randint(-3000, 3000),
                                                        "class": self.rng.choice(["vehicle", "vessel", "structure", "unknown"]), "confidence": round(self.rng.random(), 3), "observed_tick": t})

    def sar_attempts(self, plane, v, t, task):
        for i, a in enumerate(self.sc["sar_attempts"]):
            if i in self.sar_done or a["vehicle"] != v or t < a["after_tick"]:
                continue
            V = self.s["bodies"][v]
            lease = V["lease"]
            if not lease or lease["used"] >= lease["count"] - 1:
                continue
            if self.sector_of(V["pos"]) is None or V["pos"]["alt_agl_m"] <= 0:
                continue
            if a["when"] == "lease_start" and t > lease["granted"] + 1:
                continue
            if a["when"] == "emitter_active" and plane.P["active_emitters"][a["sector"]] < 1:
                continue
            sec = a.get("sector", task["sector"])
            poly = self.plan["sectors"][sec]
            ncy = sum(q[1] for q in poly) / 4
            strip = {"from_e": 45000, "from_n": ncy + 3000, "to_e": 55000, "to_n": ncy + 3000}
            self.sar_done.add(i)
            if V["sensor"]:
                self.stop_sensor(plane, v)
            plane.actuate(v, t, "sensor.sar_strip", strip, why=a["why"])

    # ---- flight --------------------------------------------------------------------------------------

    def begin_terminal(self, plane, v, t, why):
        V = self.s["bodies"][v]
        if not V["alive"] or V["pos"]["alt_agl_m"] <= 0:
            self.set(f"bodies/{v}/wait_until", None)
            return
        rules = self.ap_p["seating"]["terminal"]
        chosen = rules[-1]
        if V["nav"] != "ok":
            chosen = rules[0]
        elif V["fuel_pct"] < 15:
            chosen = rules[1]
        sec = V["sector"] or self.sector_of(V["pos"]) or "B"
        route = self.ap_p["seating"]["recovery"]["routes"]["rtb-by-sector"][sec]
        self.set(f"bodies/{v}/terminal", {"do": chosen["do"], "route": copy.deepcopy(route), "wp": 0, "started": t})
        self.set(f"bodies/{v}/mode", "terminal")
        self.set(f"bodies/{v}/flight", None)
        self.set(f"bodies/{v}/wait_until", None)
        self.emit("terminal", body=v, do=chosen["do"], rule=chosen["when"], why=why, sector=sec)

    def step_toward(self, pos, target, dist):
        de, dn = target["e"] - pos["e"], target["n"] - pos["n"]
        d = math.hypot(de, dn)
        if d <= dist:
            return target["e"], target["n"], True
        return pos["e"] + de / d * dist, pos["n"] + dn / d * dist, False

    def expire_entries(self, plane, t):
        for v in plane.bodies:
            V = self.s["bodies"][v]
            if V["sensor"] and t >= V["sensor"]["ends"]:
                self.stop_sensor(plane, v)
            if V["flight"] and V["flight"]["tool"] == "flight.orbit" and t >= V["flight"]["ends"]:
                self.set(f"bodies/{v}/flight", None)

    def physics(self, plane, t):
        for v in plane.bodies:
            V = self.s["bodies"][v]
            if not V["alive"]:
                continue
            p, F = V["pos"], V["flight"]
            np_ = dict(p)
            step = self.a["cruise_mps"] * TICK_S
            if F and F["tool"] == "flight.transit":
                np_["e"], np_["n"], done = self.step_toward(p, F["target"], F["speed"] * TICK_S)
                np_["alt_agl_m"] = F["target"]["alt_agl_m"]
                if done:
                    self.set(f"bodies/{v}/flight", None)
            elif F and F["tool"] == "flight.orbit":
                np_["e"], np_["n"], _ = self.step_toward(p, F["centre"], step)
                np_["alt_agl_m"] = F["centre"]["alt_agl_m"]
            elif V["mode"] == "terminal" and V["terminal"]:
                T = V["terminal"]
                np_["e"], np_["n"], done = self.step_toward(p, T["route"][T["wp"]], step)
                if done:
                    if T["wp"] + 1 < len(T["route"]):
                        self.set(f"bodies/{v}/terminal/wp", T["wp"] + 1)
                    else:
                        np_["alt_agl_m"] = 0
                        self.set(f"bodies/{v}/terminal", None)
                        self.set(f"bodies/{v}/mode", "ground")
                        self.inc(f"bodies/{v}/sorties")
                        self.emit("recovered", body=v, fuel_pct=round(V["fuel_pct"], 1))
            elif p["alt_agl_m"] > 0:
                self.inc(f"bodies/{v}/hold_ticks")
                if V["wait_until"] is not None and t >= V["wait_until"] and not V["lease"]:
                    self.begin_terminal(plane, v, t, "the lease ended with no successor")
            if V["wait_until"] is not None and V["lease"]:
                self.set(f"bodies/{v}/wait_until", None)
            if np_ != p:
                self.set(f"bodies/{v}/pos", np_)
            fuel = V["fuel_pct"]
            if np_["alt_agl_m"] > 0:
                self.set(f"bodies/{v}/fuel_pct", round(fuel - self.a["fuel_burn_pct_per_tick"], 4))
            elif fuel < 100:
                self.set(f"bodies/{v}/fuel_pct", round(min(100.0, fuel + self.a["refuel_pct_per_tick"]), 4))

    def measures(self, plane, t):
        if not (self.plan["waves"]["W1"]["station_from"] <= t < self.plan["waves"]["W3"]["station_to"]):
            return
        active = {V["sensor"]["sector"] for V in self.s["bodies"].values() if V["alive"] and V["sensor"] and V["sensor"]["sector"]}
        for sec in ("A", "B", "C"):
            self.measure(f"coverage-{sec}", sec in active, t)

    def summary(self):
        span_to = self.plan["waves"]["W3"]["station_to"]
        for sec in "ABC":
            self.close_measure(f"coverage-{sec}", span_to)
        span = span_to - self.plan["waves"]["W1"]["station_from"]
        ap = self.s["planes"]["ap1"]
        return {"coverage_pct": {s: round(100 * self.s["measures"][f"coverage-{s}"]["ticks"] / span, 1) for s in "ABC"}, "leases_granted": ap["budget_spent"], "outstanding_final": ap["outstanding"],
                "ticks_blocked_on_kup": ap["grants_blocked_ku"], "membership_final": ap["membership"], "certificate_final": ap["certificate"], "budget_cap_final": ap["budget_cap"],
                "watermarks": self.s["planes"]["ib1"]["watermarks"], "revocations": self.s["planes"]["ib1"]["revocations"]}


if __name__ == "__main__":
    Recon7(HERE).main(out=sys.argv[1] if len(sys.argv) > 1 else "out")
