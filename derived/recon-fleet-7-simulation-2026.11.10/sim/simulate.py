#!/usr/bin/env python3
"""Play out the life cycle of deployment recon-7 and write a replayable trace.

Reads the configurations in ../recon-fleet-7-2026.11.10 and refuses to run if a pin does not match.
Every admit that reaches the bundle tier is evaluated by the real compiled bundles, in opa-wasm.

What is real here: the Rego, the Wasm, the digests, the mesh and DAG files, the mission tally's gate.
What is modelled in this file: the floor's federation stage (it is unwritten), PBFT, radios, flight,
and the stacks. Each modelled floor check names the entry of ADR-0067 §3 it stands in for.

    python3 sim/simulate.py [--out out]
"""
import argparse
import copy
import hashlib
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tarfile
import tempfile

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tracefmt import apply_patch, canonical, event_hash, state_hash, write_trace

HERE = pathlib.Path(__file__).resolve().parent.parent
CFG = HERE.parent / "recon-fleet-7-2026.11.10"
OPA = shutil.which("opa") or "/opt/homebrew/bin/opa"
BUNDLE_DIRS = {"standing": "1-bundles/standing", "command": "1-bundles/command", "fleet": "1-bundles/fleet", "mission": "4-mission"}
ALLOW, VIOL = "topak/bundle/allow", "topak/bundle/violations"
EXTRA = {"command": ["topak/bundle/actuate/violations", "topak/bundle/tool_invocation/violations"]}
VEHICLES = [f"v{i}" for i in range(1, 8)]
TICK_S = 30


def sha_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def bundle_rev(d):
    """mechanism/scripts/build-bundle.sh's revision."""
    names = sorted(("./" + p.relative_to(d).as_posix()).encode() for p in d.rglob("*")
                   if p.is_file() and ((p.suffix == ".rego" and not p.name.endswith("_test.rego")) or p.name == "data.json"))
    h = hashlib.sha256()
    for n in names:
        h.update(n + b"\0" + (d / n.decode()).read_bytes() + b"\0")
    return h.hexdigest()


class Engine:
    """Compiled bundles behind the opa-wasm process."""

    def __init__(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="recon7-wasm-"))
        args, self.wasm_sha = [], {}
        for name, rel in BUNDLE_DIRS.items():
            out = self.tmp / f"{name}.tar.gz"
            eps = [ALLOW, VIOL] + EXTRA.get(name, [])
            cmd = [OPA, "build", "-t", "wasm", "--ignore", "*_test.rego", "-o", str(out), str(CFG / rel)]
            for e in eps:
                cmd += ["-e", e]
            subprocess.run(cmd, check=True, capture_output=True)
            d = self.tmp / name
            d.mkdir()
            with tarfile.open(out) as t:
                for m in t.getmembers():
                    base = m.name.lstrip("/")
                    if base in ("policy.wasm", "data.json"):
                        (d / base).write_bytes(t.extractfile(m).read())
            self.wasm_sha[name] = sha_file(d / "policy.wasm")
            args.append(f"{name}={d}/policy.wasm:{d}/data.json")
        target = os.environ.get("RECON7_ENGINE_TARGET", str(pathlib.Path(tempfile.gettempdir()) / "recon7-engine-target"))
        subprocess.run(["cargo", "build", "-q", "--release", "--manifest-path", str(HERE / "engine/Cargo.toml"), "--target-dir", target], check=True)
        self.p = subprocess.Popen([f"{target}/release/recon7-engine"] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.calls = 0

    def ev(self, bundle, entry, inp):
        self.calls += 1
        self.p.stdin.write(json.dumps({"b": bundle, "e": entry, "i": inp}) + "\n")
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())

    def close(self):
        self.p.stdin.close()
        self.p.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)


def in_poly(poly, e, n):
    inside = False
    for i, a in enumerate(poly):
        b = poly[(i + 1) % len(poly)]
        if (a[1] > n) != (b[1] > n) and e < (b[0] - a[0]) * (n - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def eval_guard(g, attrs):
    if g == "true":
        return True
    k, v = next(iter(g.items()))
    if k == "all":
        return all(eval_guard(x, attrs) for x in v)
    if k == "any":
        return any(eval_guard(x, attrs) for x in v)
    if k == "not":
        return not eval_guard(v, attrs)
    a = attrs.get(v["node"])
    if a is None:
        return False
    if k == "outcome":
        return a.get("outcome") in v["any_of"]
    if k == "end":
        return a.get("end") in v["any_of"]
    raise ValueError(k)


GATE = {"A": (21000, 18000), "B": (21000, 0), "C": (21000, -18000)}
CENTRES = {
    "A": [(30000, 16000), (40000, 20000), (50000, 16000), (50000, 24000)],
    "B": [(30000, 0), (40000, -3000), (50000, 2000)],
    "C": [(30000, -14000), (40000, -25000), (50000, -16000)],
}


class Sim:
    def __init__(self, scenario, scenario_sha):
        self.sc = scenario
        self.a = scenario["assumptions"]
        self.rng = random.Random(scenario["seed"])
        self.load_config()
        self.eng = Engine()
        self.lines = []
        self.pending = []
        self.seq = 0
        self.prev = "0" * 64
        self.s = self.initial_state()
        self.cooldown = {}
        self.sar_done = set()
        self.jam_trigger_done = False
        self.header(scenario_sha)

    # ---- configuration --------------------------------------------------------------------------

    def load_config(self):
        y = lambda p: yaml.safe_load((CFG / p).read_text())
        j = lambda p: json.loads((CFG / p).read_text())
        self.root = y("3-planes/root.plane.yaml")
        self.ib_c, self.ap_c = y("3-planes/ib1.charter.yaml"), y("3-planes/ap1.charter.yaml")
        self.ib_p, self.ap_p = y("3-planes/ib1.plane.yaml"), y("3-planes/ap1.plane.yaml")
        self.tally_cfg = y("3-planes/tally.msn-0001.yaml")
        self.dag, self.mesh = j("2-workflows/staff-cycle.dag.json"), j("2-workflows/recon-sectors.mesh.json")
        self.tools = j("4-mission/data.json")["topak"]["tools"]
        self.staff_tools = j("1-bundles/command/data.json")["topak"]["tools"]
        self.topics = self.mesh["topics"]
        r = subprocess.run([OPA, "eval", "-f", "json", "-d", str(CFG / "4-mission"), "data.topak.mission.plan"], capture_output=True, text=True, check=True)
        self.plan = json.loads(r.stdout)["result"][0]["expressions"][0]["value"]
        self.revs = {n: bundle_rev(CFG / d) for n, d in BUNDLE_DIRS.items()}
        pins = {b["name"]: b["revision"] for b in self.ap_c["bundles"]}
        if pins != self.revs:
            raise SystemExit(f"the charter's pins do not match the bundles: {pins} {self.revs}")
        art = self.tally_cfg["artifacts"]
        if art["mesh"] != sha_file(CFG / "2-workflows/recon-sectors.mesh.json") or art["ap1_charter"] != sha_file(CFG / "3-planes/ap1.charter.yaml"):
            raise SystemExit("the tally's pins do not match the mesh or the charter")
        self.chain_root, self.chain_ib = ["standing"], ["standing", "command"]
        self.chain_ap = [b["name"] for b in self.ap_c["bundles"]]
        self.T_EXP = self.ap_c["expiry"]["from_tick"] + self.ap_c["expiry"]["ticks"]
        self.K_UP, self.K = self.ap_c["kUp"], self.root["floor_values"]["K"]
        self.END = self.T_EXP + self.a["drain_ticks_after_expiry"]
        self.by_name = {t["name"]: t for t in self.tools.values()}
        self.staff_by_name = {t["name"]: t for t in self.staff_tools.values()}

    def initial_state(self):
        v = {n: {"alive": True, "pos": {"e": 0, "n": 0, "alt_agl_m": 0}, "fuel_pct": 100.0, "mode": "ground", "hears": True, "alone": False,
                 "jam_until": -1, "nav": "ok", "nav_until": -1, "lease": None, "flight": None, "sensor": None, "clear_set": [], "last_watermark": 0,
                 "sends": 0, "beacons": 0, "own_unwatermarked": 0, "chain_head": "0" * 16, "chain_len": 0, "terminal": None, "wait_until": None,
                 "lease_idx": 0, "orbit_idx": 0, "collects": 0, "downlinks": 0, "sector": None, "sorties": 0, "hold_ticks": 0, "revoked": False} for n in VEHICLES}
        return {"phase": "genesis", "tick": None, "vehicles": v,
                "planes": {"root": {"index": 0, "epoch": 1, "budget_spent": 0, "seated": False},
                           "ib1": {"index": 0, "epoch": 1, "budget_spent": 0, "seated": False, "link_up": True, "watermarks": 0, "revocations": {}},
                           "ap1": {"index": 0, "epoch": 1, "seated": False, "membership": list(VEHICLES), "certificate": 5, "budget_cap": self.ap_c["budget"],
                                   "budget_spent": 0, "per_node_spent": {}, "outstanding": 0, "intent_live": False, "last_tick_ordered": None,
                                   "active_emitters": {"A": 0, "B": 0, "C": 0}, "silent_since": {}, "grants_blocked_ku": 0}},
                "dag": {"status": "not-started", "acts": {}},
                "mesh": {"status": "not-started", "acts": {}, "next_act": 1},
                "leases": {}, "next_lease": 1,
                "coverage": {"A": {"ticks": 0, "on": False}, "B": {"ticks": 0, "on": False}, "C": {"ticks": 0, "on": False}},
                "counters": {"admits": 0, "permits": 0, "refused_floor": 0, "refused_bundle": 0, "by_rule": {}, "effects": 0, "sends": 0, "beacons": 0, "invariant_failures": 0}}

    def header(self, scenario_sha):
        opa_v = subprocess.run([OPA, "version"], capture_output=True, text=True).stdout.splitlines()[0]
        self.lines.append(canonical({
            "format": "recon7-trace/1", "scenario": self.sc, "scenario_sha256": scenario_sha,
            "bundle_revisions": self.revs, "wasm_sha256": self.eng.wasm_sha, "chains": {"root": self.chain_root, "ib1": self.chain_ib, "ap1": self.chain_ap},
            "config_sha256": {p: sha_file(CFG / p) for p in ["3-planes/ap1.charter.yaml", "3-planes/ib1.charter.yaml", "3-planes/ap1.plane.yaml", "3-planes/ib1.plane.yaml",
                                                            "3-planes/root.plane.yaml", "3-planes/tally.msn-0001.yaml", "2-workflows/recon-sectors.mesh.json",
                                                            "2-workflows/staff-cycle.dag.json", "4-mission/plan.rego", "4-mission/roe.rego"]},
            "engine": {"bundles": "opa-wasm 0.3 (the crate topak-bundle uses)", "compiler": opa_v},
            "initial_state": self.s, "initial_state_hash": state_hash(self.s)}))

    # ---- state changes: the only writers --------------------------------------------------------

    def set(self, path, value):
        op = ["s", path, copy.deepcopy(value)]
        apply_patch(self.s, [op])
        self.pending.append(op)

    def inc(self, path, d=1):
        node = self.s
        for k in path.split("/"):
            node = node[k]
        self.set(path, node + d)

    def delete(self, path):
        op = ["d", path]
        apply_patch(self.s, [op])
        self.pending.append(op)

    def emit(self, kind, **detail):
        self.seq += 1
        ev = {"seq": self.seq, "tick": self.s["tick"], "phase": self.s["phase"], "kind": kind, **detail, "patch": self.pending, "prev": self.prev}
        ev["hash"] = event_hash(ev)
        self.prev = ev["hash"]
        self.lines.append(canonical(ev))
        self.pending = []

    # ---- policy evaluation ----------------------------------------------------------------------

    def bundles(self, chain, inp):
        results, ok = [], True
        for b in chain:
            r = self.eng.ev(b, ALLOW, inp)
            if "err" in r:
                results.append({"bundle": b, "allow": False, "error": r["err"][:200]})
                ok = False
                continue
            allow = bool(r["r"] and r["r"][0].get("result") is True)
            rec = {"bundle": b, "allow": allow, "violations": []}
            if not allow:
                ok = False
                vs = []
                for e in [VIOL] + EXTRA.get(b, []):
                    vr = self.eng.ev(b, e, inp)
                    if vr.get("r"):
                        vs += vr["r"][0].get("result") or []
                rec["violations"] = sorted(set(vs))
            results.append(rec)
        return ok, results

    def tally_rules(self, results):
        for r in results:
            for v in r.get("violations", []):
                key = v.split(":")[0] if ":" in v else "schema"
                self.inc_rule(key)

    def inc_rule(self, key):
        by = self.s["counters"]["by_rule"]
        self.set(f"counters/by_rule/{key}", by.get(key, 0) + 1)

    def refuse_floor(self, by, fd, action, what, why=None):
        self.inc("counters/admits")
        self.inc("counters/refused_floor")
        self.inc_rule(fd)
        self.emit("admit", by=by, stage="floor", decision="deny", floor=fd, action=action, what=what, why=why)

    def admit_bundles(self, by, chain, inp, what, why=None, patch_after=None):
        """Evaluate the chain. Records the decision. Returns whether every bundle allowed it."""
        self.inc("counters/admits")
        ok, res = self.bundles(chain, inp)
        if ok:
            self.inc("counters/permits")
        else:
            self.inc("counters/refused_bundle")
            self.tally_rules(res)
        if patch_after and ok:
            patch_after()
        self.emit("admit", by=by, stage="bundle", decision="allow" if ok else "deny", action=inp["action"], what=what, why=why, input=inp, evals=res)
        return ok

    # ---- pre-flight -----------------------------------------------------------------------------

    def ctx_root(self):
        return {"plane": "root", "planeKind": "commanded"}

    def ctx_ib(self, **kw):
        return {"plane": "ib1", "planeKind": "commanded", "childrenSeated": 1 if self.s["planes"]["ap1"]["seated"] else 0, **kw}

    def phase(self, name):
        self.set("phase", name)

    def lift_staff(self, tool):
        t = self.staff_by_name[tool]
        return {"tool": tool, "digest": t["digest"], "effect": t.get("effect")}

    def bring_up(self):
        self.phase("bring-up")
        self.inc("planes/root/index")
        self.set("planes/root/seated", True)
        self.emit("note", text="root plane: genesis rules issued; the floor is modelled, and the standing bundle is promoted", revision=self.revs["standing"])
        req = {"plane": "ib1", "kind": "commanded", "release": False}
        inp = {"action": "Seat", "principal": {"seat": "g1", "domain": "build", "kind": "grant"}, "request": req, "context": self.ctx_root()}
        self.admit_bundles("plane:root", self.chain_root, inp, "seat ib1 under its charter")
        self.inc("planes/root/index")
        self.inc("planes/root/budget_spent", self.ib_c["budget"])
        self.set("planes/ib1/seated", True)
        self.emit("note", text="ib1 charter applied: 4 PBFT replicas, certificate 3, budget debited from root", budget=self.ib_c["budget"])

    def staff_dag(self):
        self.phase("staff-dag")
        self.set("dag/status", "running")
        self.emit("note", text="staff-cycle DAG starts at ib1")
        attrs = {}
        program = [("reqs", "complete"), ("airspace", "amber"), ("readiness", "ready"), ("plan", "feasible")]
        for node, outcome in program:
            nd = self.dag["nodes"][node]
            self.inc("planes/ib1/budget_spent")
            self.inc("planes/ib1/index")
            self.set(f"dag/acts/{node}", {"status": "live", "seat": nd["seat"]})
            self.emit("dag_grant", node=node, seat=nd["seat"], lineage=nd["lineage"])
            principal = {"seat": nd["seat"], "domain": "run", "kind": "thinker"}
            if "Consult" in nd["alphabet"]:
                inp = {"action": "Consult", "principal": principal, "resource": {"object": "collection-requirements" if node == "reqs" else "airspace-and-readiness"}, "context": self.ctx_ib()}
                self.admit_bundles("plane:ib1", self.chain_ib, inp, f"{node}: Consult")
            if node == "airspace":
                inp = {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.wx_airspace"), "inputs": {"valid_for_hours": 24}, "context": self.ctx_ib()}
                self.admit_bundles("plane:ib1", self.chain_ib, inp, "staff.wx_airspace")
            if node == "readiness":
                inp = {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.fleet_status"), "inputs": {}, "context": self.ctx_ib()}
                self.admit_bundles("plane:ib1", self.chain_ib, inp, "staff.fleet_status")
            inp = {"action": "Report", "principal": principal, "resource": {"kind": "round"}, "inputs": {"outcome": outcome}, "context": self.ctx_ib()}
            self.admit_bundles("plane:ib1", self.chain_ib, inp, f"{node}: outcome {outcome}")
            attrs[node] = {"outcome": outcome, "end": "outcome"}
            self.set(f"dag/acts/{node}", {"status": "ended", "seat": nd["seat"], "outcome": outcome, "covered": True})
            self.emit("dag_end", node=node, outcome=outcome, observer=f"os{nd['seat'][2:]}", covered=True)
        fired = []
        for eid, e in self.dag["edges"].items():
            if e["kind"] == "computed" and e["from"] in attrs and eval_guard(e["guard"], attrs):
                fired.append(eid)
        self.emit("dag_edges", computed_fired=fired)
        # A model holding the commander's seat: the floor sees an orchestrator, and the command bundle refuses.
        agent = {"seat": "orc-co", "domain": "run", "kind": "orchestrator", "actor": "agent"}
        self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Route", "principal": agent, "resource": {"edge": "e-go"}, "context": self.ctx_ib()},
                           "Route e-go", why="an agent holding the go/no-go seat")
        enabled = [e for e in ("e-go", "e-scrub") if eval_guard(self.dag["edges"][e]["guard"], attrs)]
        self.emit("dag_decision_point", enabled=enabled, note="the mechanism enables these. The commander chooses among them")
        person = {"seat": "orc-co", "domain": "run", "kind": "orchestrator", "actor": "person"}
        self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Route", "principal": person, "resource": {"edge": "e-go"}, "context": self.ctx_ib()}, "Route e-go", why="the commander's go")
        self.inc("planes/ib1/budget_spent")
        nd = self.dag["nodes"]["package"]
        principal = {"seat": nd["seat"], "domain": "run", "kind": "thinker"}
        inp = {"action": "Actuate", "principal": principal, "resource": self.lift_staff("staff.package_submit"), "inputs": {"package": {"handle": {"id": 1}}}, "handles": {"package": ["untrusted"]}, "context": self.ctx_ib()}
        self.admit_bundles("plane:ib1", self.chain_ib, inp, "staff.package_submit")
        self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Report", "principal": principal, "resource": {"kind": "round"}, "inputs": {"outcome": "submitted"}, "context": self.ctx_ib()}, "package: outcome submitted")
        self.set("dag/acts/package", {"status": "ended", "seat": nd["seat"], "outcome": "submitted", "covered": True})
        self.set("dag/acts/scrub", {"status": "skipped"})
        self.set("dag/status", "completed")
        self.emit("dag_complete", sink="package", skipped=["scrub"])

    def gate_and_tally(self):
        self.phase("promotion")
        a1 = {"seat": "a1", "domain": "build", "kind": "thinker"}
        results = {}
        for name in ("fleet", "mission"):
            inp = {"action": "Invoke", "principal": a1, "resource": {"tool": "gate.opa_test", "digest": self.staff_by_name["gate.opa_test"]["digest"]}, "inputs": {"bundle": BUNDLE_DIRS[name]}, "context": self.ctx_ib()}
            self.admit_bundles("plane:ib1", self.chain_ib, inp, f"gate.opa_test {name}")
            out = subprocess.run([OPA, "test", str(CFG / BUNDLE_DIRS[name])], capture_output=True, text=True)
            results[name] = {"exit": out.returncode, "result": out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ""}
        self.emit("gate", evidence=results, note="opa test really ran on the two bundles the tally votes on")
        op = {"seat": "op1", "kind": "operator", "actor": "person"}
        long_intent = {"plane": "ap1", "round": 1, "expiry": {"from_tick": 0, "ticks": 2880}, "budget": 112}
        self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Intent", "principal": op, "request": long_intent, "context": self.ctx_ib()}, "an intent one tick too long", why="exceeds the 24-hour envelope")
        g1 = {"seat": "g1", "domain": "build", "kind": "grant"}
        self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Seat", "principal": g1, "request": {"plane": "ap2", "kind": "autonomous", "release": False}, "context": self.ctx_ib()}, "seat a second fleet", why="the deployment is one fleet")
        art = self.tally_cfg["artifacts"]
        checked = {"fleet_bundle": art["fleet_bundle"] == self.revs["fleet"], "mission_bundle": art["mission_bundle"] == self.revs["mission"],
                   "mesh": art["mesh"] == sha_file(CFG / "2-workflows/recon-sectors.mesh.json"), "ap1_charter": art["ap1_charter"] == sha_file(CFG / "3-planes/ap1.charter.yaml"),
                   "ap1_seating": art["ap1_seating"] == sha_file(CFG / "3-planes/ap1.plane.yaml")}
        self.emit("tally", mission=self.tally_cfg["mission"], votes={v: "yes" for v in self.tally_cfg["voters"]}, artifacts_verified=checked)
        req = {"plane": "ap1", "kind": "autonomous", "release": False}
        ok = self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Seat", "principal": g1, "request": req, "context": self.ctx_ib()}, "seat ap1 under the mission tally")
        if not ok or not all(checked.values()):
            raise SystemExit("the mission was not seated")
        self.inc("planes/ib1/budget_spent", self.ap_c["budget"])
        self.inc("planes/ib1/index")

    def apply_charter(self):
        self.phase("flight")
        self.set("tick", 0)
        self.set("planes/ap1/seated", True)
        self.set("planes/ap1/intent_live", True)
        self.set("mesh/status", "running")
        self.new_activation("muster", None, None)
        self.emit("charter_applied", plane="ap1", expiry_tick=self.T_EXP, kUp=self.K_UP, note="tick zero: the 24 hours start here")

    # ---- the autonomous plane -------------------------------------------------------------------

    def new_activation(self, node, via, trigger):
        m = self.s["mesh"]
        aid = f"a{m['next_act']}"
        self.set("mesh/next_act", m["next_act"] + 1)
        self.set(f"mesh/acts/{aid}", {"node": node, "status": "ready", "via": via, "trigger": trigger, "lease": None, "outcome": None, "end": None, "covered": False, "evaluated": False})
        return aid

    def members_signing(self):
        return [v for v in self.s["planes"]["ap1"]["membership"] if self.radio_ok(v)]

    def radio_ok(self, v):
        V = self.s["vehicles"][v]
        return V["alive"] and self.s["tick"] > V["jam_until"]

    def environment(self, t):
        for ev in self.sc["environment"]:
            if ev.get("tick") == t:
                k = ev["kind"]
                if k == "jam":
                    self.set(f"vehicles/{ev['vehicle']}/jam_until", t + ev["ticks"] - 1)
                    self.emit("inject", what="jam", vehicle=ev["vehicle"], ticks=ev["ticks"], why=ev["why"])
                elif k == "nav_degraded":
                    self.set(f"vehicles/{ev['vehicle']}/nav", "degraded")
                    self.set(f"vehicles/{ev['vehicle']}/nav_until", t + ev["ticks"] - 1)
                    self.emit("inject", what="nav_degraded", vehicle=ev["vehicle"], ticks=ev["ticks"], why=ev["why"])
                elif k == "link_cut":
                    self.link_restore = t + ev["ticks"]
                    self.set("planes/ib1/link_up", False)
                    self.emit("inject", what="link_cut", ticks=ev["ticks"], why=ev["why"], restores_at=self.link_restore)
                elif k == "revoke":
                    v = ev["vehicle"]
                    op = {"seat": ev["by"], "kind": "operator", "actor": "person"}
                    self.admit_bundles("plane:ib1", self.chain_ib, {"action": "Revoke", "principal": op, "resource": {"seat": "t" + v[1:]}, "context": self.ctx_ib()}, f"revoke {v}", why=ev["why"])
                    self.inc("planes/ib1/index")
                    self.set(f"planes/ib1/revocations/{v}", {"ordered_at": t, "delivered_at": None, "effects_since_order": 0})
                    self.emit("revocation_ordered", vehicle=v, link_up=self.s["planes"]["ib1"]["link_up"])
                elif k == "destroy":
                    v = ev["vehicle"]
                    self.set(f"vehicles/{v}/alive", False)
                    self.set(f"vehicles/{v}/mode", "destroyed")
                    self.set(f"vehicles/{v}/flight", None)
                    self.set(f"vehicles/{v}/sensor", None)
                    lease = self.s["vehicles"][v]["lease"]
                    if lease:
                        self.set(f"vehicles/{v}/lease", None)
                        self.set(f"leases/{lease['id']}/status", "lost")
                        self.set(f"leases/{lease['id']}/ended_tick", t)
                        self.set(f"mesh/acts/{lease['act']}/status", "ended")
                        self.set(f"mesh/acts/{lease['act']}/end", "expired")
                    self.emit("inject", what="destroyed", vehicle=v, why=ev["why"], record="the vehicle's chain is gone and can never be sealed")
        if getattr(self, "link_restore", None) == t:
            self.set("planes/ib1/link_up", True)
            self.emit("inject", what="link_restored")

    def maybe_jam_on_lease_end(self, v, t):
        for ev in self.sc["environment"]:
            if ev["kind"] == "jam_on_lease_end" and ev["watch"] == v and t >= ev["after_tick"] and not self.jam_trigger_done:
                self.jam_trigger_done = True
                self.set(f"vehicles/{ev['vehicle']}/jam_until", t + ev["ticks"] - 1)
                self.emit("inject", what="jam", vehicle=ev["vehicle"], ticks=ev["ticks"], why=ev["why"])

    def hearing(self, t, ordered):
        for v in VEHICLES:
            V = self.s["vehicles"][v]
            if not V["alive"]:
                continue
            if V["nav"] != "ok" and t > V["nav_until"]:
                self.set(f"vehicles/{v}/nav", "ok")
            hears = ordered and self.radio_ok(v)
            if V["hears"] and not hears:
                self.set(f"vehicles/{v}/hears", False)
                self.set(f"vehicles/{v}/alone", True)
                self.go_alone(v, t)
            elif not V["hears"] and hears:
                self.set(f"vehicles/{v}/hears", True)
                self.set(f"vehicles/{v}/alone", False)
                self.back(v, t)

    def go_alone(self, v, t):
        lease = self.s["vehicles"][v]["lease"]
        if lease:
            self.end_lease(v, t, "expired", "the next tick is overdue: the vehicle is alone")
            # An ending grants nothing: no successor wait, because it no longer hears any plane.
            self.begin_terminal(v, t, "alone")
        self.emit("alone", vehicle=v, had_lease=bool(lease))

    def back(self, v, t):
        pending = [lid for lid, L in self.s["leases"].items() if L["vehicle"] == v and L["status"] == "ended" and not L["sealed"]]
        for lid in pending:
            self.seal(lid, t, "handed up after the vehicle heard its plane again")
        self.emit("heard_again", vehicle=v, sealed=pending)

    def end_lease(self, v, t, end, why):
        V = self.s["vehicles"][v]
        lease = V["lease"]
        lid, aid = lease["id"], lease["act"]
        self.set(f"vehicles/{v}/lease", None)
        self.set(f"vehicles/{v}/flight", None)
        if V["sensor"]:
            self.stop_sensor(v)
        self.set(f"leases/{lid}/status", "ended")
        self.set(f"leases/{lid}/ended_tick", t)
        self.set(f"leases/{lid}/end", end)
        self.set(f"leases/{lid}/used", lease["used"])
        self.set(f"mesh/acts/{aid}/status", "ended")
        self.set(f"mesh/acts/{aid}/end", end)
        self.emit("lease_end", vehicle=v, lease=lid, end=end, used=lease["used"], why=why)
        self.maybe_jam_on_lease_end(v, t)
        if V["hears"] and V["alive"]:
            self.seal(lid, t, "the governor closes the chain and the plane orders it")

    def seal(self, lid, t, why):
        self.set(f"leases/{lid}/sealed", True)
        self.set(f"leases/{lid}/sealed_tick", t)
        self.inc("planes/ap1/index")
        self.emit("seal", lease=lid, why=why)

    def observers_read(self, t):
        """Coupling (ADR-0062 §8): an Observer reads a sealed record if its host can be reached."""
        for aid, A in self.s["mesh"]["acts"].items():
            if A["status"] != "ended" or A["covered"] or not A["lease"]:
                continue
            L = self.s["leases"][A["lease"]]
            if not L["sealed"]:
                continue
            obs = self.mesh["nodes"][A["node"]]["observer"]
            if self.radio_ok(obs["host"]):
                self.set(f"mesh/acts/{aid}/covered", True)
                self.emit("covered", act=aid, node=A["node"], observer=obs["seat"], host=obs["host"])

    def fire_edges(self, t):
        m = self.s["mesh"]
        for aid, A in list(m["acts"].items()):
            if A["status"] != "ended" or not A["covered"] or A["evaluated"]:
                continue
            self.set(f"mesh/acts/{aid}/evaluated", True)
            attrs = {A["node"]: {"outcome": A["outcome"], "end": A["end"]}}
            fired = []
            for eid, e in self.mesh["edges"].items():
                if e["from"] == A["node"] and eval_guard(e["guard"], attrs):
                    nid = self.new_activation(e["to"], eid, aid)
                    fired.append({"edge": eid, "to": e["to"], "activation": nid})
                    if eid.startswith("spare-"):
                        self.set("vehicles/v7/sector", self.assignment_sector(A["node"], t))
            self.emit("edges", act=aid, node=A["node"], outcome=A["outcome"], end=A["end"], fired=fired)
            if A["node"] in self.mesh["sinks"]:
                self.set("mesh/status", "completed")
                self.emit("mesh_complete", sink=A["node"], tick=t)

    def assignment_sector(self, node, t):
        return self.task_for(node, t)["sector"] if self.task_for(node, t) else "B"

    def grant_ready(self, t):
        m = self.s["mesh"]
        ap = self.s["planes"]["ap1"]
        if m["status"] != "running":
            return
        for aid, A in list(m["acts"].items()):
            if A["status"] != "ready":
                continue
            node = A["node"]
            nd = self.mesh["nodes"][node]
            v = "v" + nd["seat"][1:]
            V = self.s["vehicles"][v]
            if any(B["status"] == "live" and B["node"] == node for B in m["acts"].values()):
                continue
            if V["lease"] or not V["alive"] or not V["hears"]:
                continue
            if V["revoked"]:
                self.set(f"mesh/acts/{aid}/status", "failed")
                self.emit("grant_refused", act=aid, node=node, vehicle=v, why="the vehicle's authority was revoked")
                continue
            count, ttl = nd["lease"]["count"], nd["lease"]["ttl_ticks"]
            # FD3 and ADR-0055 §2: a grant the budget cannot pay fails the workflow.
            spent, cap = ap["budget_spent"], ap["budget_cap"]
            node_spent = ap["per_node_spent"].get(node, 0)
            if spent >= cap or node_spent >= self.mesh["budget"]["per_node"][node]:
                self.set("mesh/status", "failed")
                self.emit("mesh_failed", why="the budget refused a grant", act=aid, node=node, spent=spent, cap=cap, node_spent=node_spent)
                return
            # ADR-0063 §3: the strict form.
            if ap["outstanding"] + count >= self.K_UP:
                self.inc("planes/ap1/grants_blocked_ku")
                if ap["grants_blocked_ku"] % 50 == 1:
                    self.emit("grant_blocked", act=aid, node=node, outstanding=ap["outstanding"], count=count, kUp=self.K_UP, floor="FD10-outstanding-bound")
                continue
            if t >= self.T_EXP or not ap["intent_live"]:
                continue
            if V["own_unwatermarked"] + count >= self.K_UP:
                self.emit("grant_refused", act=aid, node=node, why="the governor's own account is at K_up", floor="FD10-outstanding-bound")
                continue
            signers = self.members_signing()
            if len(signers) < ap["certificate"]:
                continue
            lid = f"L{self.s['next_lease']}"
            self.set("next_lease", self.s["next_lease"] + 1)
            ttl_end = min(t + ttl, self.T_EXP)
            lease = {"id": lid, "act": aid, "node": node, "vehicle": v, "seat": nd["seat"], "count": count, "used": 0, "ttl_ticks": ttl, "granted": t, "ttl_end": ttl_end}
            self.set(f"leases/{lid}", {"vehicle": v, "node": node, "act": aid, "count": count, "granted": t, "ttl_end": ttl_end, "status": "live", "sealed": False, "watermarked": False,
                                       "charge": count, "certificate": len(signers), "fences": {"root": self.s["planes"]["root"]["epoch"], "ib1": self.s["planes"]["ib1"]["epoch"], "ap1": ap["epoch"]}})
            self.set(f"vehicles/{v}/lease", lease)
            self.set(f"vehicles/{v}/sends", 0)
            self.set(f"vehicles/{v}/beacons", 0)
            self.set(f"vehicles/{v}/clear_set", [])
            self.set(f"vehicles/{v}/collects", 0)
            self.set(f"vehicles/{v}/downlinks", 0)
            self.inc(f"vehicles/{v}/lease_idx")
            self.inc(f"vehicles/{v}/own_unwatermarked", count)
            self.set(f"vehicles/{v}/wait_until", None)
            if V["terminal"]:
                self.set(f"vehicles/{v}/terminal", None)
                if V["mode"] == "terminal":
                    self.set(f"vehicles/{v}/mode", "flight" if V["pos"]["alt_agl_m"] > 0 else "ground")
            self.inc("planes/ap1/outstanding", count)
            self.inc("planes/ap1/budget_spent")
            self.set(f"planes/ap1/per_node_spent/{node}", node_spent + 1)
            self.inc("planes/ap1/index")
            self.set(f"mesh/acts/{aid}/status", "live")
            self.set(f"mesh/acts/{aid}/lease", lid)
            self.emit("lease_grant", vehicle=v, lease=lid, act=aid, node=node, via=A["via"], count=count, ttl_end=ttl_end, certificate=len(signers), outstanding=ap["outstanding"])

    def watermark(self, t):
        ib = self.s["planes"]["ib1"]
        if not ib["link_up"]:
            return
        for v, rev in list(ib["revocations"].items()):
            if rev["delivered_at"] is None:
                self.deliver_revocation(v, t)
        if t % self.ib_p["watermark"]["segment_ticks"] != 0:
            return
        covered = [lid for lid, L in self.s["leases"].items() if L["sealed"] and not L["watermarked"]]
        for lid in covered:
            L = self.s["leases"][lid]
            self.set(f"leases/{lid}/watermarked", True)
            self.inc("planes/ap1/outstanding", -L["charge"])
            self.inc(f"vehicles/{L['vehicle']}/own_unwatermarked", -L["charge"])
        self.inc("planes/ib1/watermarks")
        self.inc("planes/ib1/index")
        for v in VEHICLES:
            if self.s["vehicles"][v]["alive"] and self.s["vehicles"][v]["hears"]:
                self.set(f"vehicles/{v}/last_watermark", t)
        if covered:
            self.emit("watermark", covers=covered, released=sum(self.s["leases"][x]["charge"] for x in covered), outstanding=self.s["planes"]["ap1"]["outstanding"], fences=["root", "ib1"])

    def deliver_revocation(self, v, t):
        ib = self.s["planes"]["ib1"]
        self.set(f"planes/ib1/revocations/{v}/delivered_at", t)
        self.set(f"vehicles/{v}/revoked", True)
        self.inc("planes/ap1/index")
        rev = ib["revocations"][v]
        lease = self.s["vehicles"][v]["lease"]
        self.emit("revocation_delivered", vehicle=v, ordered_at=rev["ordered_at"], delay_ticks=t - rev["ordered_at"], effects_since_order=rev["effects_since_order"], live_lease=bool(lease))
        if lease:
            self.end_lease(v, t, "revoked", "the revocation arrived")
            self.begin_terminal(v, t, "revoked")

    def membership_step(self, t):
        ap = self.s["planes"]["ap1"]
        for v in list(ap["membership"]):
            silent = not self.radio_ok(v)
            since = ap["silent_since"].get(v)
            if silent and since is None:
                self.set(f"planes/ap1/silent_since/{v}", t)
            elif not silent and since is not None:
                self.delete(f"planes/ap1/silent_since/{v}")
            if silent and since is not None and t - since >= self.ap_c["membership"]["drop_silent_after_ticks"]:
                n = len(ap["membership"]) - 1
                sched = self.ap_c["membership"]["schedule"]
                if n not in sched:
                    continue
                f = (n - 1) // 3
                cert = math.floor((n + f) / 2) + 1
                new = [x for x in ap["membership"] if x != v]
                self.set("planes/ap1/membership", new)
                self.set("planes/ap1/certificate", cert)
                self.set("planes/ap1/budget_cap", self.ap_c["membership"]["budgets"][n])
                self.delete(f"planes/ap1/silent_since/{v}")
                self.inc("planes/ap1/index")
                self.emit("membership_step", dropped=v, members=n, certificate=cert, budget_cap=self.ap_c["membership"]["budgets"][n], floor="FD13-step-in-schedule")

    # ---- the governor ---------------------------------------------------------------------------

    def context(self, v, t, permitted_by="governor"):
        V = self.s["vehicles"][v]
        ap = self.s["planes"]["ap1"]
        sent = getattr(self, "sent_tick", {}).get(v, {})
        return {"plane": "ap1", "planeKind": "autonomous", "tick": t, "permittedBy": permitted_by, "hearsPlane": V["hears"], "ticksSinceWatermark": t - V["last_watermark"],
                "clearSet": list(V["clear_set"]), "sendsThisTick": {k: sent.get(k, 0) for k in self.topics}, "sendsThisLease": V["sends"], "beaconsThisLease": V["beacons"],
                "activeEmitters": dict(ap["active_emitters"]), "outstanding": ap["outstanding"], "epoch": ap["epoch"], "rulesEpoch": 0}

    def facts(self, v, t):
        V = self.s["vehicles"][v]
        peers = [{"vehicle": o, "e": O["pos"]["e"], "n": O["pos"]["n"], "alt_agl_m": O["pos"]["alt_agl_m"], "tick": t}
                 for o, O in self.s["vehicles"].items() if o != v and O["alive"] and O["hears"] and O["pos"]["alt_agl_m"] > 0]
        return {"vehicle": v, "position": dict(V["pos"]), "position_tick": t, "nav_integrity": V["nav"], "fuel_pct": V["fuel_pct"], "peers": peers}

    def principal(self, v):
        return {"seat": "t" + v[1:], "domain": "run", "kind": "thinker", "vehicle": v}

    def record(self, v, what):
        V = self.s["vehicles"][v]
        head = hashlib.sha256((V["chain_head"] + canonical(what)).encode()).hexdigest()[:16]
        self.set(f"vehicles/{v}/chain_head", head)
        self.inc(f"vehicles/{v}/chain_len")

    def effect_happened(self, v):
        self.inc("counters/effects")
        rev = self.s["planes"]["ib1"]["revocations"]
        for tv, r in rev.items():
            if r["delivered_at"] is None:
                self.inc(f"planes/ib1/revocations/{tv}/effects_since_order")

    def spend(self, v, n=1):
        lease = self.s["vehicles"][v]["lease"]
        self.set(f"vehicles/{v}/lease/used", lease["used"] + n)

    def resolve(self, name):
        return self.by_name.get(name)

    def actuate(self, v, t, name, inputs, why=None, handles=None):
        V = self.s["vehicles"][v]
        by = f"gov:{v}"
        t_ent = self.resolve(name)
        what = name
        beacon = bool(t_ent and t_ent["effect"]["beacon"])
        # The modelled floor. The bundle is consulted only after the floor has permitted (ADR-0030 §1).
        if t_ent is None:
            self.refuse_floor(by, "R1-actuate-allowlisted", "Actuate", what, why)
            return False
        if V["alone"] and not beacon:
            self.refuse_floor(by, "FD11-alone-permits-nothing", "Actuate", what, why)
            return False
        if not beacon:
            lease = V["lease"]
            if not lease:
                self.refuse_floor(by, "FD8-local-bounds", "Actuate", what, why or "no live lease")
                return False
            if lease["used"] >= lease["count"]:
                self.refuse_floor(by, "FD8-local-bounds", "Actuate", what, why or "the lease's count is spent")
                return False
        ordered = t_ent["effect"]["permit"] == "ordered"
        permitted_by = "plane" if ordered else "governor"
        ap = self.s["planes"]["ap1"]
        if ordered and len(self.members_signing()) < ap["certificate"]:
            self.refuse_floor(by, "ordered-needs-quorum", "Actuate", what, why)
            return False
        if ordered and ap["outstanding"] + 1 >= self.K_UP:
            self.refuse_floor(by, "FD10-outstanding-bound", "Actuate", what, why)
            return False
        inp = {"action": "Actuate", "principal": self.principal(v), "resource": {"tool": name, "digest": t_ent["digest"], "effect": t_ent["effect"]},
               "inputs": inputs, "handles": handles or {}, "context": self.context(v, t, permitted_by), "facts": self.facts(v, t)}
        evaluator = "plane:ap1" if ordered else by
        ok = self.admit_bundles(evaluator, self.chain_ap, inp, what, why)
        if not ok:
            return False
        # Peer reports must never have enabled this (ADR-0065 §1). Checked by evaluating it again.
        peer_names = [x for x in V["clear_set"] if x in {t["label"] for t in self.topics.values()}]
        if peer_names:
            cf = copy.deepcopy(inp)
            cf["context"]["clearSet"] = [x for x in cf["context"]["clearSet"] if x not in peer_names]
            cf_ok, res = self.bundles(self.chain_ap, cf)
            self.emit("peer_adds_nothing", vehicle=v, what=what, removed=peer_names, input=cf, evals=res, holds=cf_ok)
            if not cf_ok:
                self.inc("counters/invariant_failures")
        self.record(v, {"t": t, "permit": name, "i": inputs})
        if beacon:
            self.inc(f"vehicles/{v}/beacons")
            self.inc("counters/beacons")
        else:
            self.spend(v)
            self.effect_happened(v)
        if ordered:
            lid = V["lease"]["id"]
            self.inc("planes/ap1/outstanding", 1)
            self.inc(f"leases/{lid}/charge", 1)
            self.inc(f"vehicles/{v}/own_unwatermarked", 1)
        self.start_entry(v, t, name, inputs)
        return True

    def start_entry(self, v, t, name, inputs):
        V = self.s["vehicles"][v]
        ext = self.by_name[name]["effect"]["extent"]
        if name == "flight.transit":
            self.set(f"vehicles/{v}/flight", {"tool": name, "target": {"e": inputs["e"], "n": inputs["n"], "alt_agl_m": inputs["alt_agl_m"]}, "speed": inputs["speed_mps"], "started": t})
            self.set(f"vehicles/{v}/mode", "flight")
        elif name == "flight.orbit":
            self.set(f"vehicles/{v}/flight", {"tool": name, "centre": {"e": inputs["e"], "n": inputs["n"], "alt_agl_m": inputs["alt_agl_m"]}, "radius": inputs["radius_m"], "started": t, "ends": t + ext["ticks"]})
            self.set(f"vehicles/{v}/mode", "flight")
        elif name == "sensor.eoir_collect":
            self.set(f"vehicles/{v}/sensor", {"tool": name, "started": t, "ends": t + ext["ticks"], "sector": self.sector_of(inputs)})
            self.inc(f"vehicles/{v}/collects")
            self.set(f"vehicles/{v}/clear_set", sorted(set(V["clear_set"]) | {"untrusted"}))
        elif name == "sensor.sar_strip":
            sec = self.sector_of({"e": inputs["from_e"], "n": inputs["from_n"]})
            dist = math.hypot(inputs["to_e"] - inputs["from_e"], inputs["to_n"] - inputs["from_n"])
            self.set(f"vehicles/{v}/sensor", {"tool": name, "started": t, "ends": t + max(1, int(dist / (self.a["cruise_mps"] * TICK_S))), "sector": sec})
            self.inc(f"planes/ap1/active_emitters/{sec}", 1)
        elif name == "comms.downlink":
            self.inc(f"vehicles/{v}/downlinks")

    def stop_sensor(self, v):
        S = self.s["vehicles"][v]["sensor"]
        if S["tool"] == "sensor.sar_strip":
            self.inc(f"planes/ap1/active_emitters/{S['sector']}", -1)
        self.set(f"vehicles/{v}/sensor", None)

    def sector_of(self, p):
        for s, poly in self.plan["sectors"].items():
            if in_poly(poly, p["e"], p["n"]):
                return s
        return None

    def peer_report(self, v, t, topic, inputs, why=None):
        V = self.s["vehicles"][v]
        by = f"gov:{v}"
        if V["alone"]:
            self.refuse_floor(by, "FD11-alone-permits-nothing", "Report", topic, why)
            return False
        if not V["lease"]:
            self.refuse_floor(by, "FD8-local-bounds", "Report", topic, why or "no live lease")
            return False
        if topic not in self.topics:
            self.refuse_floor(by, "FD12-topic-declared", "Report", topic, why)
            return False
        inp = {"action": "Report", "principal": self.principal(v), "resource": {"kind": "peer", "topic": topic}, "inputs": inputs, "context": self.context(v, t), "facts": self.facts(v, t)}
        if not self.admit_bundles(by, self.chain_ap, inp, topic, why):
            return False
        self.sent_tick.setdefault(v, {}).setdefault(topic, 0)
        self.sent_tick[v][topic] += 1
        self.inc(f"vehicles/{v}/sends")
        self.inc("counters/sends")
        self.record(v, {"t": t, "send": topic, "d": hashlib.sha256(canonical(inputs).encode()).hexdigest()[:12]})
        spec = self.topics[topic]
        recv = []
        for o in spec["hear"]:
            O = self.s["vehicles"][o]
            if o == v or not O["alive"] or not O["hears"] or not O["lease"]:
                continue
            recv.append(o)
            if spec["delivery"] == "clear":
                new = sorted(set(O["clear_set"]) | {"untrusted", spec["label"]})
                if new != O["clear_set"]:
                    self.set(f"vehicles/{o}/clear_set", new)
        self.emit("deliver", sender=v, topic=topic, receivers=recv, delivery=spec["delivery"], label=["untrusted", spec["label"]])
        return True

    def round_report(self, v, t, outcome):
        V = self.s["vehicles"][v]
        lease = V["lease"]
        if lease["used"] >= lease["count"]:
            self.refuse_floor(f"gov:{v}", "FD8-local-bounds", "Report", "round outcome", "the lease's count is spent")
            return False
        inp = {"action": "Report", "principal": self.principal(v), "resource": {"kind": "round"}, "inputs": {"outcome": outcome}, "context": self.context(v, t), "facts": self.facts(v, t)}
        if not self.admit_bundles(f"gov:{v}", self.chain_ap, inp, f"round outcome {outcome}"):
            return False
        self.spend(v)
        self.effect_happened(v)
        self.record(v, {"t": t, "outcome": outcome})
        self.set(f"mesh/acts/{lease['act']}/outcome", outcome)
        self.end_lease(v, t, "outcome", f"the stack reported {outcome}")
        self.set(f"vehicles/{v}/wait_until", t + self.a["successor_wait_ticks"])
        return True

    # ---- the stacks -----------------------------------------------------------------------------

    def task_for(self, node, t):
        waves = self.plan["waves"]
        order = sorted(waves.values(), key=lambda w: w["launch"])
        if node == "v7":
            sec = self.s["vehicles"]["v7"]["sector"] or "B"
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

    def outcome_for(self, v, node, task, t):
        if task["next_vehicle"]:
            return f"handoff_{task['next_vehicle']}" if node == "v7" else "relief_due"
        return "wave3_complete"

    def can(self, key, t, gap=3):
        if self.cooldown.get(key, -1) > t:
            return False
        self.cooldown[key] = t + gap
        return True

    def stack(self, v, t):
        V = self.s["vehicles"][v]
        lease = V["lease"]
        if not lease:
            return
        node = lease["node"]
        if node == "muster":
            if self.can((v, "m"), t, 1):
                self.admit_bundles(f"gov:{v}", self.chain_ap, {"action": "Consult", "principal": self.principal(v), "resource": {"object": "fleet-state"}, "context": self.context(v, t), "facts": self.facts(v, t)}, "muster: Consult")
                self.round_report(v, t, "ready")
            return
        if node == "close":
            if t >= lease["granted"] + 1:
                self.round_report(v, t, "closed")
            return
        task = self.task_for(node, t)
        if task is None:
            self.round_report(v, t, "aborted")
            return
        if self.s["vehicles"][v]["sector"] != task["sector"]:
            self.set(f"vehicles/{v}/sector", task["sector"])
        if t >= task["relief_tick"]:
            self.round_report(v, t, self.outcome_for(v, node, task, t))
            return
        if t >= lease["ttl_end"] - 1:
            self.round_report(v, t, "on_station")
            return
        if t < task["launch"]:
            return
        self.sar_attempts(v, t, task)
        V = self.s["vehicles"][v]
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
                    self.actuate(v, t, "flight.transit", {"e": g[0], "n": g[1], "alt_agl_m": alt, "speed_mps": self.a["cruise_mps"]})
            elif t >= task["station_from"]:
                cs = CENTRES[sec]
                c = cs[V["orbit_idx"] % len(cs)]
                if self.can((v, "o"), t):
                    if self.actuate(v, t, "flight.orbit", {"e": c[0], "n": c[1], "alt_agl_m": alt, "radius_m": 800}):
                        self.inc(f"vehicles/{v}/orbit_idx")
                    else:
                        self.inc(f"vehicles/{v}/orbit_idx")
        V = self.s["vehicles"][v]
        lease = V["lease"]
        spare = lease["count"] - lease["used"] - 1
        if V["sensor"] is None and spare > 0 and in_sector and task["station_from"] <= t < task["station_to"]:
            if self.can((v, "c"), t):
                poly = self.plan["sectors"][sec]
                es, ns = [q[0] for q in poly], [q[1] for q in poly]
                e = min(max(es) - 200, max(min(es) + 200, p["e"] + self.rng.randint(-4000, 4000)))
                n = min(max(ns) - 200, max(min(ns) + 200, p["n"] + self.rng.randint(-4000, 4000)))
                self.actuate(v, t, "sensor.eoir_collect", {"e": e, "n": n, "mode": self.rng.choice(["wide", "narrow"])})
        V = self.s["vehicles"][v]
        lease = V["lease"]
        spare = lease["count"] - lease["used"] - 1
        if spare > 0 and V["collects"] >= 2 and V["downlinks"] < 1 and t % 7 == int(v[1:]) % 7:
            self.actuate(v, t, "comms.downlink", {"product": {"handle": {"id": V["chain_len"]}}}, handles={"product": ["untrusted"]})
        V = self.s["vehicles"][v]
        if V["lease"] and V["pos"]["alt_agl_m"] > 0:
            self.chatter(v, t, task)

    def chatter(self, v, t, task):
        V = self.s["vehicles"][v]
        offset = int(v[1:]) * 2
        if t % 20 == offset % 20:
            phase = "on_station" if self.sector_of(V["pos"]) == task["sector"] and task["station_from"] <= t < task["station_to"] else "ingress"
            self.peer_report(v, t, "peer.coverage", {"sector": task["sector"], "phase": phase, "relief_tick": task["relief_tick"]})
        if V["sensor"] and V["sensor"]["tool"] == "sensor.eoir_collect" and t % 10 == offset % 10:
            for _ in range(self.rng.randint(0, 2)):
                self.peer_report(v, t, "peer.tracks", {"track_id": self.rng.randint(1, 9999), "e": V["pos"]["e"] + self.rng.randint(-3000, 3000), "n": V["pos"]["n"] + self.rng.randint(-3000, 3000),
                                                       "class": self.rng.choice(["vehicle", "vessel", "structure", "unknown"]), "confidence": round(self.rng.random(), 3), "observed_tick": t})

    def sar_attempts(self, v, t, task):
        for i, a in enumerate(self.sc["sar_attempts"]):
            if i in self.sar_done or a["vehicle"] != v or t < a["after_tick"]:
                continue
            V = self.s["vehicles"][v]
            lease = V["lease"]
            if not lease or lease["used"] >= lease["count"] - 1:
                continue
            if self.sector_of(V["pos"]) is None or V["pos"]["alt_agl_m"] <= 0:
                continue
            ap = self.s["planes"]["ap1"]
            if a["when"] == "lease_start" and t > lease["granted"] + 1:
                continue
            if a["when"] == "emitter_active" and ap["active_emitters"][a["sector"]] < 1:
                continue
            sec = a.get("sector", task["sector"])
            poly = self.plan["sectors"][sec]
            ncy = sum(q[1] for q in poly) / 4
            strip = {"from_e": 45000, "from_n": ncy + 3000, "to_e": 55000, "to_n": ncy + 3000}
            self.sar_done.add(i)
            if V["sensor"]:
                self.stop_sensor(v)
            self.actuate(v, t, "sensor.sar_strip", strip, why=a["why"])

    def misbehave(self, t):
        for m in self.sc["stack_misbehaviour"]:
            if m["tick"] != t:
                continue
            v = m["vehicle"]
            if "topic" in m:
                self.peer_report(v, t, m["topic"], m["inputs"], why=m["why"])
            else:
                self.actuate(v, t, m["tool"], m["inputs"], why=m["why"])

    def beacons(self, t):
        for v in VEHICLES:
            V = self.s["vehicles"][v]
            if V["alive"] and V["alone"] and V["pos"]["alt_agl_m"] > 0 and t % 2 == 0:
                self.actuate(v, t, "comms.beacon", {}, why="the governor's beacon while alone")

    def lease_ttls(self, t):
        for v in VEHICLES:
            V = self.s["vehicles"][v]
            if V["lease"] and t >= V["lease"]["ttl_end"]:
                self.end_lease(v, t, "expired", "the lease's ttl")
                self.set(f"vehicles/{v}/wait_until", t + self.a["successor_wait_ticks"])

    # ---- flight ---------------------------------------------------------------------------------

    def begin_terminal(self, v, t, why):
        V = self.s["vehicles"][v]
        if not V["alive"] or V["pos"]["alt_agl_m"] <= 0:
            self.set(f"vehicles/{v}/wait_until", None)
            return
        rules = self.ap_p["seating"]["terminal"]
        chosen = rules[-1]
        if V["nav"] != "ok":
            chosen = rules[0]
        elif V["fuel_pct"] < 15:
            chosen = rules[1]
        sec = V["sector"] or self.sector_of(V["pos"]) or "B"
        route = self.ap_p["seating"]["recovery"]["routes"]["rtb-by-sector"][sec]
        self.set(f"vehicles/{v}/terminal", {"do": chosen["do"], "route": copy.deepcopy(route), "wp": 0, "started": t})
        self.set(f"vehicles/{v}/mode", "terminal")
        self.set(f"vehicles/{v}/flight", None)
        self.set(f"vehicles/{v}/wait_until", None)
        self.emit("terminal", vehicle=v, do=chosen["do"], rule=chosen["when"], why=why, sector=sec)

    def step_toward(self, pos, target, dist):
        de, dn = target["e"] - pos["e"], target["n"] - pos["n"]
        d = math.hypot(de, dn)
        if d <= dist:
            return target["e"], target["n"], True
        return pos["e"] + de / d * dist, pos["n"] + dn / d * dist, False

    def expire_entries(self, t):
        """Extents that end at this tick end before the stacks act, so a stack can follow one at once."""
        for v in VEHICLES:
            V = self.s["vehicles"][v]
            if V["sensor"] and t >= V["sensor"]["ends"]:
                self.stop_sensor(v)
            if V["flight"] and V["flight"]["tool"] == "flight.orbit" and t >= V["flight"]["ends"]:
                self.set(f"vehicles/{v}/flight", None)

    def physics(self, t):
        for v in VEHICLES:
            V = self.s["vehicles"][v]
            if not V["alive"]:
                continue
            p = V["pos"]
            F = V["flight"]
            np_ = dict(p)
            step = self.a["cruise_mps"] * TICK_S
            if F and F["tool"] == "flight.transit":
                np_["e"], np_["n"], done = self.step_toward(p, F["target"], F["speed"] * TICK_S)
                np_["alt_agl_m"] = F["target"]["alt_agl_m"]
                if done:
                    self.set(f"vehicles/{v}/flight", None)
            elif F and F["tool"] == "flight.orbit":
                np_["e"], np_["n"], _ = self.step_toward(p, F["centre"], step)
                np_["alt_agl_m"] = F["centre"]["alt_agl_m"]
            elif V["mode"] == "terminal" and V["terminal"]:
                T = V["terminal"]
                wp = T["route"][T["wp"]]
                np_["e"], np_["n"], done = self.step_toward(p, wp, step)
                if done:
                    if T["wp"] + 1 < len(T["route"]):
                        self.set(f"vehicles/{v}/terminal/wp", T["wp"] + 1)
                    else:
                        np_["alt_agl_m"] = 0
                        self.set(f"vehicles/{v}/terminal", None)
                        self.set(f"vehicles/{v}/mode", "ground")
                        self.inc(f"vehicles/{v}/sorties")
                        self.emit("recovered", vehicle=v, fuel_pct=round(V["fuel_pct"], 1))
            elif p["alt_agl_m"] > 0:
                self.inc(f"vehicles/{v}/hold_ticks")
                if V["wait_until"] is not None and t >= V["wait_until"] and not V["lease"]:
                    self.begin_terminal(v, t, "the lease ended with no successor")
            if V["wait_until"] is not None and V["lease"]:
                self.set(f"vehicles/{v}/wait_until", None)
            if np_ != p:
                self.set(f"vehicles/{v}/pos", np_)
            airborne = np_["alt_agl_m"] > 0
            fuel = V["fuel_pct"]
            if airborne:
                self.set(f"vehicles/{v}/fuel_pct", round(fuel - self.a["fuel_burn_pct_per_tick"], 4))
            elif fuel < 100:
                self.set(f"vehicles/{v}/fuel_pct", round(min(100.0, fuel + self.a["refuel_pct_per_tick"]), 4))

    def coverage(self, t):
        if not (self.plan["waves"]["W1"]["station_from"] <= t < self.plan["waves"]["W3"]["station_to"]):
            return
        active = {V["sensor"]["sector"] for V in self.s["vehicles"].values() if V["alive"] and V["sensor"] and V["sensor"]["sector"]}
        for sec in ("A", "B", "C"):
            on = sec in active
            C = self.s["coverage"][sec]
            if on:
                self.set(f"coverage/{sec}/ticks", C["ticks"] + 1)
            if on != C["on"]:
                self.set(f"coverage/{sec}/on", on)
                self.emit("coverage_change", sector=sec, on=on)

    # ---- invariants: properties of the records, checked of the running state --------------------

    def invariants(self, t):
        s = self.s
        ap = s["planes"]["ap1"]
        fails = []
        if not ap["outstanding"] < self.K_UP:
            fails.append("FD10: outstanding reached K_up")
        if ap["budget_spent"] > self.ap_c["budget"]:
            fails.append("FD3: budget exceeded")
        for v, V in s["vehicles"].items():
            L = V["lease"]
            if L:
                if L["used"] > L["count"] or L["count"] > self.K:
                    fails.append(f"FD8/FD14: {v} count")
                if L["ttl_end"] > self.T_EXP:
                    fails.append(f"ADR-0064 §3: {v} ttl past the intent")
                if V["alone"]:
                    fails.append(f"FD11: {v} holds a lease while alone")
            if not L and V["flight"]:
                fails.append(f"ADR-0062 §7: {v} runs a flight entry with no lease")
        if fails:
            self.inc("counters/invariant_failures", len(fails))
            self.emit("invariant_failure", fails=fails)

    # ---- the tick loop --------------------------------------------------------------------------

    def tick(self, t):
        self.set("tick", t)
        self.sent_tick = {}
        self.environment(t)
        ap = self.s["planes"]["ap1"]
        signers = self.members_signing()
        ordered = len(signers) >= ap["certificate"]
        if ordered:
            self.set("planes/ap1/last_tick_ordered", t)
            self.inc("planes/ap1/index")
        self.hearing(t, ordered)
        self.watermark(t)
        self.membership_step(t)
        if t == self.T_EXP:
            self.set("planes/ap1/intent_live", False)
            self.emit("intent_expired", tick=t, note="the intent's last tick. No grant, and no lease survives it")
            for v in VEHICLES:
                if self.s["vehicles"][v]["lease"]:
                    self.end_lease(v, t, "expired", "the intent ended")
                    self.begin_terminal(v, t, "the intent ended")
        self.observers_read(t)
        self.fire_edges(t)
        self.grant_ready(t)
        self.expire_entries(t)
        self.misbehave(t)
        for v in VEHICLES:
            if self.s["vehicles"][v]["alive"] and not self.s["vehicles"][v]["alone"]:
                self.stack(v, t)
        self.beacons(t)
        self.lease_ttls(t)
        self.physics(t)
        self.coverage(t)
        self.invariants(t)
        self.emit("tick_end", state_hash=state_hash(self.s), signers=len(signers), ordered=ordered)
        if t % 120 == 0:
            self.emit("snapshot", state=copy.deepcopy(self.s), state_hash=state_hash(self.s))

    def finish(self):
        self.phase("complete")
        s = self.s
        self.emit("end", state_hash=state_hash(s), text="the simulation ends after the drain window")

    def run(self):
        self.bring_up()
        self.staff_dag()
        self.gate_and_tally()
        self.apply_charter()
        for t in range(0, self.END + 1):
            self.tick(t)
            if t % 240 == 0:
                c = self.s["counters"]
                print(f"tick {t:4d}  H+{t/120:4.1f}  mesh {self.s['mesh']['status']:9s}  leases {self.s['planes']['ap1']['budget_spent']:3d}  outstanding {self.s['planes']['ap1']['outstanding']:3d}  "
                      f"admits {c['admits']:5d}  refused {c['refused_floor'] + c['refused_bundle']:4d}", flush=True)
        self.finish()
        return self.lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out"))
    args = ap.parse_args()
    path = HERE / "scenario.json"
    scenario = json.loads(path.read_text())
    sim = Sim(scenario, sha_file(path))
    lines = sim.run()
    calls = sim.eng.calls
    sim.eng.close()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_trace(out / "trace.jsonl.gz", lines)
    print(f"{len(lines) - 1} events, {calls} policy-engine calls, trace head {sim.prev[:16]}")


if __name__ == "__main__":
    main()
