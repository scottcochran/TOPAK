#!/usr/bin/env python3
"""Replay a use-case trace with no simulator and no random numbers. From a simulation's directory:

    python3 -m topak_sim.replay                     check the hash chain, rebuild the state, compare every state hash
    python3 -m topak_sim.replay --reeval rego       also re-decide every bundle decision with the Rego interpreter
    python3 -m topak_sim.replay --reeval wasm       also re-decide every bundle and linked-floor decision with the engine
    python3 -m topak_sim.replay --at 1800           print the state at a tick (--path bodies/v1 narrows it)
    python3 -m topak_sim.replay --timeline          print what happened
    python3 -m topak_sim.replay --admits v3 --from 160 --to 200     print the admits of one principal
    python3 -m topak_sim.replay --explain 1234      print one event in full
    python3 -m topak_sim.replay --summary           print the outcome as JSON

Only the patches change state. The policy decisions in the trace are records, and --reeval checks them.
"""
import argparse
import hashlib
import http.client
import json
import pathlib
import subprocess
import sys
import time

from .policy import OPA, Engine
from .trace import apply_patch, event_hash, read_trace, state_hash

SKIP_FIELDS = ("seq", "tick", "phase", "kind", "patch", "prev", "hash", "input", "evals", "state", "state_hash", "floor", "summary")


def stamp(header, t):
    if t is None:
        return "pre"
    s = header.get("tick_seconds")
    if not s:
        return f"t{t}"
    m = t * s // 60
    return f"H+{m // 60:02d}:{m % 60:02d}"


def rebuild(header, events, stop_at=None):
    """Applies patches in order, checking the chain. Returns the state, any errors and the hashes compared."""
    state = json.loads(json.dumps(header["initial_state"]))
    errors = []
    if state_hash(state) != header["initial_state_hash"]:
        errors.append("the initial state does not match its hash")
    prev, hashes = "0" * 64, 0
    for ev in events:
        if ev["prev"] != prev:
            errors.append(f"event {ev['seq']}: broken chain")
        if event_hash(ev) != ev["hash"]:
            errors.append(f"event {ev['seq']}: altered")
        prev = ev["hash"]
        if stop_at is not None and ev["tick"] is not None and ev["tick"] > stop_at:
            break
        apply_patch(state, ev["patch"])
        if ev["kind"] in ("tick_end", "snapshot", "end"):
            hashes += 1
            if state_hash(state) != ev["state_hash"]:
                errors.append(f"event {ev['seq']} tick {ev['tick']}: state hash differs")
        if ev["kind"] == "snapshot" and json.dumps(ev["state"], sort_keys=True) != json.dumps(state, sort_keys=True):
            errors.append(f"event {ev['seq']}: snapshot differs from the replayed state")
    return state, errors, hashes


class Rego:
    def __init__(self, cfg, bundles):
        self.spec, self.procs, self.conns = bundles, [], {}
        for i, (name, b) in enumerate(bundles.items()):
            port = 28181 + i
            self.procs.append(subprocess.Popen([OPA, "run", "--server", "--addr", f"127.0.0.1:{port}", "--ignore", "*_test.rego", str(cfg / b["dir"])], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            for _ in range(100):
                try:
                    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                    c.request("GET", "/health")
                    if c.getresponse().read() is not None:
                        break
                except OSError:
                    time.sleep(0.1)
            self.conns[name] = http.client.HTTPConnection("127.0.0.1", port, timeout=30)

    def query(self, b, path, inp):
        c = self.conns[b]
        c.request("POST", f"/v1/data/{path}", json.dumps({"input": inp}), {"Content-Type": "application/json"})
        return json.loads(c.getresponse().read()).get("result")

    def decide(self, b, inp):
        allow = self.query(b, "topak/bundle/allow", inp) is True
        vs = []
        if not allow:
            for p in ["topak/bundle/violations"] + self.spec[b].get("extra_violations", []):
                vs += self.query(b, p, inp) or []
        return {"allow": allow, "violations": sorted(set(vs))}

    def close(self):
        for p in self.procs:
            p.terminate()


def reevaluate(header, events, kind, cfg):
    spec = header["deployment"]["bundles"]
    eng = Rego(cfg, spec) if kind == "rego" else Engine(cfg, spec)
    n = f = diffs = 0
    try:
        for ev in events:
            for rec in ev.get("evals", []):
                n += 1
                got = eng.decide(rec["bundle"], ev["input"]) if kind == "rego" else eng.bundle(rec["bundle"], ev["input"])
                if got["allow"] != rec["allow"] or sorted(got["violations"]) != sorted(rec.get("violations", [])):
                    diffs += 1
                    print(f"DIFF event {ev['seq']} {rec['bundle']}: recorded {rec['allow']} {rec.get('violations')} now {got['allow']} {got['violations']}")
            fl = ev.get("floor") if ev["kind"] == "admit" else {}
            if kind == "wasm" and fl.get("engine") == "cedar":
                f += 1
                out = eng.floor(fl["request"])
                if out["permit"] != fl["permit"] or sorted(out.get("reasons", [])) != sorted(fl.get("reasons", [])):
                    diffs += 1
                    print(f"DIFF event {ev['seq']} floor: recorded {fl['permit']} {fl.get('reasons')} now {out['permit']} {out.get('reasons')}")
    finally:
        eng.close()
    return n, f, diffs


def describe(ev):
    d = {k: v for k, v in ev.items() if k not in SKIP_FIELDS}
    if ev["kind"] == "note":
        return d["text"]
    return f"{ev['kind']} " + " ".join(f"{a}={b}" for a, b in d.items() if b is not None)


def reasons(ev):
    out = [v for r in ev.get("evals", []) for v in r.get("violations", [])]
    fl = ev.get("floor") or {}
    if ev.get("stage") == "floor":
        out += [fl["rule"]] if fl.get("rule") else fl.get("reasons") or ["floor: no permit"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", default="out/trace.jsonl.gz")
    ap.add_argument("--sim", default=".", help="the simulation's directory, which the trace's configuration path is relative to")
    ap.add_argument("--reeval", choices=["rego", "wasm"])
    ap.add_argument("--at", type=int)
    ap.add_argument("--path")
    ap.add_argument("--timeline", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--admits")
    ap.add_argument("--from", dest="frm", type=int, default=0)
    ap.add_argument("--to", type=int, default=10**9)
    ap.add_argument("--explain", type=int)
    a = ap.parse_args()
    header, events = read_trace(a.trace)
    cfg = (pathlib.Path(a.sim).resolve() / header["deployment"]["config"]).resolve()
    if a.timeline:
        skip = set(header["timeline_skip"])
        for ev in events:
            if ev["kind"] not in skip:
                print(f"{stamp(header, ev['tick']):>9} {'' if ev['tick'] is None else 't' + str(ev['tick']):<7} {describe(ev)}")
            elif ev["kind"] == "admit" and ev["decision"] == "deny":
                print(f"{stamp(header, ev['tick']):>9} {'' if ev['tick'] is None else 't' + str(ev['tick']):<7} REFUSED {ev['by']} {ev['what']}: {'; '.join(reasons(ev))}")
        return None
    if a.explain:
        return print(json.dumps(next(e for e in events if e["seq"] == a.explain), indent=2, ensure_ascii=False))
    if a.admits:
        for ev in events:
            if ev["kind"] == "admit" and a.admits in ev.get("by", "") and a.frm <= (ev["tick"] or 0) <= a.to:
                print(f"#{ev['seq']:<6} {stamp(header, ev['tick']):>9} t{ev['tick']} {ev['decision']:5} {ev['what']:28} {'; '.join(reasons(ev))}")
        return None
    if a.at is not None:
        state, errors, _ = rebuild(header, events, stop_at=a.at)
        for e in errors:
            print(e)
        node = state
        for k in (a.path or "").split("/") if a.path else []:
            node = node[int(k) if isinstance(node, list) else k]
        return print(json.dumps(node, indent=1, sort_keys=True, ensure_ascii=False))
    state, errors, hashes = rebuild(header, events)
    if a.summary:
        end = next((e for e in reversed(events) if e["kind"] == "end"), {})
        return print(json.dumps({"scenario": header["scenario"]["name"], "seed": header["scenario"]["seed"], "events": len(events), "counters": state["counters"],
                                 "workflows": {k: v["status"] for k, v in state["workflows"].items()}, "measures": state["measures"], "summary": end.get("summary")}, indent=2, sort_keys=True))
    print(f"{len(events)} events; hash chain and {hashes} state hashes {'OK' if not errors else 'FAILED'}")
    for e in errors[:20]:
        print(" ", e)
    for p, want in header["config_sha256"].items():
        f = cfg / p
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != want:
            print(f"  note: {p} has changed since this trace was recorded")
    bad = len(errors)
    if a.reeval:
        n, f, diffs = reevaluate(header, events, a.reeval, cfg)
        print(f"re-evaluated {n} bundle decisions and {f} floor decisions with {a.reeval}: {diffs} differences")
        bad += diffs
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
