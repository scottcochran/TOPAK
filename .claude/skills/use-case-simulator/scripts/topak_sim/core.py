"""The recorder, the admission path, pins, scenarios and the tick loop.

A world subclasses Core. State changes go only through set, inc, delete and sync, and reach the trace
only through emit, which is why a trace can be replayed with no simulator.
"""
import copy
import json
import pathlib
import random
import subprocess

from .policy import OPA, Engine, bundle_rev, sha_file
from .trace import FORMAT, apply_patch, canonical, diff, event_hash, state_hash, write_trace

try:
    import yaml
except ImportError:
    yaml = None


class Core:
    snapshot_every = 120
    tick_seconds = None  # set this, and replay shows elapsed time as H+hh:mm
    timeline_skip = ("tick_end", "snapshot", "admit", "covered", "seal", "peer_adds_nothing", "edges", "deliver")

    def __init__(self, sim_dir, scenario="scenario.json"):
        self.dir = pathlib.Path(sim_dir).resolve()
        path = self.dir / scenario
        self.sc = json.loads(path.read_text())
        self.dep = self.sc["deployment"]
        self.cfg = (self.dir / self.dep["config"]).resolve()
        self.a = self.sc.get("assumptions", {})
        self.rng = random.Random(self.sc["seed"])
        self.revs = {n: bundle_rev(self.cfg / b["dir"]) for n, b in self.dep["bundles"].items()}
        self.chains = self.dep["chains"]
        self.verify_pins()
        self.load()
        self.eng = Engine(self.cfg, self.dep["bundles"])
        self.lines, self.pending, self.seq, self.prev = [], [], 0, "0" * 64
        self.s = {"phase": "genesis", "tick": None, "workflows": {}, "measures": {},
                  "counters": {"admits": 0, "permits": 0, "refused_floor": 0, "refused_bundle": 0, "by_rule": {}, "invariant_failures": 0}}
        self.s.update(self.initial_state())
        self.header(sha_file(path))

    # ---- what a world provides ------------------------------------------------------------------

    def load(self):
        """Read the configuration into attributes. Runs before the engine starts."""

    def initial_state(self):
        return {}

    def preflight(self):
        """Everything before the first tick: bring-up, staff work, the promotion. Load workflows here,
        since the header is already written and a load is an event."""

    def step(self, t):
        """One tick. May return a dict, recorded on the tick's closing event."""
        return {}

    def last_tick(self):
        return -1

    def summary(self):
        """What this world's run came to. Recorded in the trace, so replay needs no knowledge of the world."""
        return {}

    # ---- configuration ----------------------------------------------------------------------------

    def load_cfg(self, rel):
        p = self.cfg / rel
        if p.suffix == ".json":
            return json.loads(p.read_text())
        if yaml is None:
            raise SystemExit("this configuration needs PyYAML: uv run --with pyyaml ...")
        return yaml.safe_load(p.read_text())

    def rego_value(self, bundle, ref):
        """A constant out of a bundle's Rego, so the simulation cannot disagree with the policy about it."""
        r = subprocess.run([OPA, "eval", "-f", "json", "-d", str(self.cfg / self.dep["bundles"][bundle]["dir"]), ref], capture_output=True, text=True, check=True)
        return json.loads(r.stdout)["result"][0]["expressions"][0]["value"]

    def verify_pins(self):
        """Refuse to run a configuration that is not the one its charters and tallies pin."""
        def at(doc, path):
            for k in path.split("/"):
                doc = doc[k]
            return doc

        for pin in self.dep.get("pins", []):
            doc = self.load_cfg(pin["in"])
            kind, value = pin["kind"], at(doc, pin["at"])
            if kind == "bundle_list":
                got = {b["name"]: b["revision"] for b in value}
                want = {n: self.revs[n] for n in got}
                if got != want:
                    raise SystemExit(f"{pin['in']} pins bundles that do not match: {got} against {want}")
            elif kind == "bundle":
                if value != self.revs[pin["bundle"]]:
                    raise SystemExit(f"{pin['in']}:{pin['at']} does not pin bundle {pin['bundle']}'s revision")
            elif kind == "file":
                if value != sha_file(self.cfg / pin["file"]):
                    raise SystemExit(f"{pin['in']}:{pin['at']} does not pin {pin['file']}")
            else:
                raise SystemExit(f"unknown pin kind {kind}")

    def header(self, scenario_sha):
        opa_v = subprocess.run([OPA, "version"], capture_output=True, text=True).stdout.splitlines()[0]
        cfg_files = sorted(p for p in self.cfg.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        self.lines.append(canonical({
            "format": FORMAT, "scenario": self.sc, "scenario_sha256": scenario_sha, "deployment": self.dep, "bundle_revisions": self.revs, "wasm_sha256": self.eng.wasm_sha,
            "config_sha256": {p.relative_to(self.cfg).as_posix(): sha_file(p) for p in cfg_files}, "engine": {"bundles": "opa-wasm 0.3", "compiler": opa_v, "floor": self.eng.info()},
            "tick_seconds": self.tick_seconds, "timeline_skip": list(self.timeline_skip), "initial_state": self.s, "initial_state_hash": state_hash(self.s)}))

    # ---- state changes: the only writers ----------------------------------------------------------

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

    def sync(self, path, new):
        """Bring a subtree in line with a value computed outside the kernel, as the smallest patch."""
        node = self.s
        for k in path.split("/"):
            node = node[int(k) if isinstance(node, list) else k]
        ops = diff(path, node, new)
        apply_patch(self.s, ops)
        self.pending += ops

    def emit(self, kind, **detail):
        self.seq += 1
        ev = {"seq": self.seq, "tick": self.s["tick"], "phase": self.s["phase"], "kind": kind, **detail, "patch": self.pending, "prev": self.prev}
        ev["hash"] = event_hash(ev)
        self.prev = ev["hash"]
        self.lines.append(canonical(ev))
        self.pending = []

    def phase(self, name):
        self.set("phase", name)

    # ---- admission: floor_permit AND NOT bundle_deny (ADR-0030 §1) -----------------------------------

    def bundles(self, chain, inp):
        res = [self.eng.bundle(b, inp) for b in chain]
        return all(r["allow"] for r in res), res

    def inc_rule(self, key):
        key = key.replace("/", "_")
        self.set(f"counters/by_rule/{key}", self.s["counters"]["by_rule"].get(key, 0) + 1)

    def tally_rules(self, results):
        for r in results:
            for v in r.get("violations", []):
                self.inc_rule(v.split(":")[0] if ":" in v else "schema")

    def refuse_modelled(self, by, rule, action, what, why=None):
        """A refusal by a check that exists in no running code. `rule` names the entry it stands in for."""
        self.inc("counters/admits")
        self.inc("counters/refused_floor")
        self.inc_rule(rule)
        self.emit("admit", by=by, stage="floor", decision="deny", floor={"engine": "modelled", "rule": rule}, action=action, what=what, why=why)

    def admit(self, by, chain, inp, what, why=None, floor=None, after=None):
        """The admit path. `floor` is a lift's floor part, evaluated by the linked floor, or None if this
        admit's floor is modelled. The bundles are consulted only once the floor has permitted."""
        self.inc("counters/admits")
        rec = None
        if floor is not None:
            out = self.eng.floor(floor)
            rec = {"engine": "cedar", "permit": out["permit"], "reasons": out.get("reasons", []), "request": floor}
            if "error" in out:
                rec["error"] = out["error"]
            if not out["permit"]:
                self.inc("counters/refused_floor")
                for r in out.get("reasons") or (["floor-error"] if "error" in out else ["floor-no-permit"]):
                    self.inc_rule(r)
                self.emit("admit", by=by, stage="floor", decision="deny", floor=rec, action=inp["action"], what=what, why=why, input=inp)
                return False
        ok, res = self.bundles(chain, inp)
        if ok:
            self.inc("counters/permits")
        else:
            self.inc("counters/refused_bundle")
            self.tally_rules(res)
        if after and ok:
            after()
        self.emit("admit", by=by, stage="bundle", decision="allow" if ok else "deny", floor=rec or {"engine": "modelled"}, action=inp["action"], what=what, why=why, input=inp, evals=res)
        return ok

    def invariant(self, ok, message):
        """A property of the records, checked of the running state."""
        if not ok:
            self.inc("counters/invariant_failures")
            self.emit("invariant_failure", fails=[message])

    # ---- interval measures: what the mission delivered ----------------------------------------------

    def measure(self, name, on, t):
        """Call once per tick over the measure's window. Tracks ticks on, and every gap, in the state."""
        path = f"measures/{name}"
        M = self.s["measures"].get(name)
        if M is None:
            self.set(path, {"ticks": 0, "on": False, "since": t, "gaps": []})
            M = self.s["measures"][name]
        if on:
            self.set(f"{path}/ticks", M["ticks"] + 1)
        if on != M["on"]:
            self.set(f"{path}/on", on)
            if on and t > M["since"]:
                self.set(f"{path}/gaps", M["gaps"] + [[M["since"], t]])
            if not on:
                self.set(f"{path}/since", t)
            self.emit("measure_change", measure=name, on=on)

    def close_measure(self, name, end):
        M = self.s["measures"][name]
        if not M["on"] and M["since"] < end:
            self.set(f"measures/{name}/gaps", M["gaps"] + [[M["since"], end]])

    # ---- the run ----------------------------------------------------------------------------------

    def tick(self, t):
        self.set("tick", t)
        extra = self.step(t) or {}
        self.emit("tick_end", state_hash=state_hash(self.s), **extra)
        if self.snapshot_every and t % self.snapshot_every == 0:
            self.emit("snapshot", state=copy.deepcopy(self.s), state_hash=state_hash(self.s))

    def run(self):
        self.preflight()
        for t in range(0, self.last_tick() + 1):
            self.tick(t)
        self.phase("complete")
        result = self.summary()
        self.emit("end", state_hash=state_hash(self.s), summary=result)
        return self.lines

    def main(self, out="out"):
        """Run, write the trace, and close the engine."""
        lines = self.run()
        calls = self.eng.calls
        self.eng.close()
        d = self.dir / out
        d.mkdir(parents=True, exist_ok=True)
        write_trace(d / "trace.jsonl.gz", lines)
        c = self.s["counters"]
        print(f"{len(lines) - 1} events, {calls} engine calls, {c['admits']} admits, {c['refused_floor'] + c['refused_bundle']} refused, "
              f"{c['invariant_failures']} invariant failures, trace head {self.prev[:16]}")
