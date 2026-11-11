#!/usr/bin/env python3
"""Replay a recon-7 trace with no simulator and no random numbers.

    replay.py                      check the hash chain, rebuild the state, compare every state hash
    replay.py --reeval rego        also re-decide every recorded admit with the Rego interpreter
    replay.py --reeval wasm        also re-decide every recorded admit with opa-wasm
    replay.py --at 1800            print the fleet at a tick
    replay.py --timeline           print what happened
    replay.py --admits v3 --from 160 --to 200     print the admits of one governor
    replay.py --explain 1234       print one event in full
    replay.py --summary            print the outcome as JSON

Only the patches change state. The policy decisions in the trace are records, and --reeval is what
checks them against the bundles.
"""
import argparse
import http.client
import json
import pathlib
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tracefmt import apply_patch, event_hash, read_trace, state_hash

HERE = pathlib.Path(__file__).resolve().parent.parent
CFG = HERE.parent / "recon-fleet-7-2026.11.10"
OPA = shutil.which("opa") or "/opt/homebrew/bin/opa"
DIRS = {"standing": "1-bundles/standing", "command": "1-bundles/command", "fleet": "1-bundles/fleet", "mission": "4-mission"}
EXTRA = {"command": ["actuate/violations", "tool_invocation/violations"]}
SKIP_TIMELINE = {"tick_end", "snapshot", "admit", "deliver", "covered", "seal", "peer_adds_nothing", "edges"}


def hhmm(t):
    if t is None:
        return "  pre  "
    return f"H+{t // 120:02d}:{(t % 120) // 2:02d}"


def rebuild(header, events, stop_at=None):
    """Applies patches in order, checking the chain. Returns the state and any errors."""
    state = json.loads(json.dumps(header["initial_state"]))
    errors = []
    if state_hash(state) != header["initial_state_hash"]:
        errors.append("the initial state does not match its hash")
    prev = "0" * 64
    hashes = 0
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
    def __init__(self):
        self.procs, self.conns = [], {}
        for i, (name, rel) in enumerate(DIRS.items()):
            port = 28181 + i
            self.procs.append(subprocess.Popen([OPA, "run", "--server", "--addr", f"127.0.0.1:{port}", "--ignore", "*_test.rego", str(CFG / rel)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
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
        c.request("POST", f"/v1/data/topak/bundle/{path}", json.dumps({"input": inp}), {"Content-Type": "application/json"})
        return json.loads(c.getresponse().read()).get("result")

    def decide(self, b, inp):
        allow = self.query(b, "allow", inp) is True
        vs = []
        if not allow:
            for p in ["violations"] + EXTRA.get(b, []):
                vs += self.query(b, p, inp) or []
        return allow, sorted(set(vs))

    def close(self):
        for p in self.procs:
            p.terminate()


class Wasm:
    def __init__(self):
        import simulate

        self.e, self.sim = simulate.Engine(), simulate

    def decide(self, b, inp):
        r = self.e.ev(b, self.sim.ALLOW, inp)
        allow = bool(r.get("r") and r["r"][0].get("result") is True)
        vs = []
        if not allow:
            for p in [self.sim.VIOL] + self.sim.EXTRA.get(b, []):
                vr = self.e.ev(b, p, inp)
                if vr.get("r"):
                    vs += vr["r"][0].get("result") or []
        return allow, sorted(set(vs))

    def close(self):
        self.e.close()


def reevaluate(events, kind):
    eng = Rego() if kind == "rego" else Wasm()
    n = diffs = 0
    try:
        for ev in events:
            if "evals" not in ev:
                continue
            for rec in ev["evals"]:
                n += 1
                allow, vs = eng.decide(rec["bundle"], ev["input"])
                if allow != rec["allow"] or vs != sorted(rec.get("violations", [])):
                    diffs += 1
                    print(f"DIFF event {ev['seq']} {rec['bundle']}: recorded {rec['allow']} {rec.get('violations')} now {allow} {vs}")
    finally:
        eng.close()
    return n, diffs


def describe(ev):
    k = ev["kind"]
    d = {x: y for x, y in ev.items() if x not in ("seq", "tick", "phase", "kind", "patch", "prev", "hash", "input", "evals", "state", "state_hash")}
    if k == "inject":
        return f"INJECT {d['what']} {d.get('vehicle', '')} {('· ' + d['why']) if d.get('why') else ''}".strip()
    if k == "lease_grant":
        return f"grant  {d['lease']} to {d['vehicle']} (node {d['node']}, via {d['via']}) count {d['count']}, ends tick {d['ttl_end']}, cert {d['certificate']}, outstanding {d['outstanding']}"
    if k == "lease_end":
        return f"end    {d['lease']} on {d['vehicle']}: {d['end']}, {d['used']} used · {d['why']}"
    if k == "grant_blocked":
        return f"BLOCKED {d['node']}: outstanding {d['outstanding']} + {d['count']} would reach K_up {d['kUp']} ({d['floor']})"
    if k == "watermark":
        return f"watermark covers {len(d['covers'])} lease(s), released {d['released']}, outstanding now {d['outstanding']}"
    if k == "terminal":
        return f"terminal {d['vehicle']}: {d['do']} (sector {d['sector']}) · {d['why']}"
    if k == "coverage_change":
        return f"sector {d['sector']} coverage {'ON' if d['on'] else 'off'}"
    if k == "recovered":
        return f"{d['vehicle']} recovered at R1, fuel {d['fuel_pct']}%"
    if k == "note":
        return d["text"]
    return f"{k} " + " ".join(f"{a}={b}" for a, b in d.items() if b is not None)


def short_gaps(events, limit=6):
    """The coverage_change pairs that bracket a gap of fewer than `limit` ticks: lease renewals."""
    skip, off = set(), {}
    for ev in events:
        if ev["kind"] != "coverage_change":
            continue
        if not ev["on"]:
            off[ev["sector"]] = ev
        elif ev["sector"] in off:
            o = off.pop(ev["sector"])
            if ev["tick"] - o["tick"] < limit:
                skip |= {o["seq"], ev["seq"]}
    return skip


def timeline(events):
    # A flight's worth of on_station renewals is the routine, so loops are collapsed unless asked.
    skip = short_gaps(events)
    for ev in events:
        if ev["kind"] in SKIP_TIMELINE or ev["seq"] in skip:
            continue
        if ev["kind"] == "lease_grant" and (ev.get("via") or "").startswith("loop-"):
            continue
        if ev["kind"] == "lease_end" and ev["end"] == "outcome" and "on_station" in ev["why"]:
            continue
        if ev["kind"] == "watermark":
            continue
        print(f"{hhmm(ev['tick'])} t{'' if ev['tick'] is None else ev['tick']:<5} {describe(ev)}")
    print("\nRefused admits by reason are in --summary. Routine renewals, watermarks and coverage gaps under 3 minutes are omitted.")


def summary(header, events, state):
    span_from, span_to = 60, 2700
    gaps = {s: [] for s in "ABC"}
    on = {s: False for s in "ABC"}
    since = {s: span_from for s in "ABC"}
    for ev in events:
        if ev["kind"] == "coverage_change":
            s = ev["sector"]
            if ev["on"]:
                if ev["tick"] > since[s]:
                    gaps[s].append([since[s], ev["tick"]])
                on[s] = True
            else:
                on[s] = False
                since[s] = ev["tick"]
    for s in "ABC":
        if not on[s] and since[s] < span_to:
            gaps[s].append([since[s], span_to])
    span = span_to - span_from
    peak = 0
    first_block = None
    allow = 0
    for ev in events:
        if ev["kind"] == "lease_grant":
            peak = max(peak, ev["outstanding"])
        if ev["kind"] == "grant_blocked" and first_block is None:
            first_block = ev["tick"]
        if ev["kind"] == "admit" and ev["decision"] == "allow":
            allow += 1
    pa = [e for e in events if e["kind"] == "peer_adds_nothing"]
    ap = state["planes"]["ap1"]
    return {
        "scenario": header["scenario"]["name"], "seed": header["scenario"]["seed"], "events": len(events),
        "policy_decisions_recorded": sum(len(e["evals"]) for e in events if "evals" in e),
        "mesh_status": state["mesh"]["status"],
        "coverage": {s: {"ticks": state["coverage"][s]["ticks"], "of": span, "pct": round(100 * state["coverage"][s]["ticks"] / span, 1), "gaps": gaps[s]} for s in "ABC"},
        "leases_granted": ap["budget_spent"], "budget": header["initial_state"]["planes"]["ap1"]["budget_cap"], "per_node_spent": ap["per_node_spent"],
        "outstanding_final": ap["outstanding"], "outstanding_peak_at_grant": peak, "first_kup_block_tick": first_block, "ticks_blocked_on_kup": ap["grants_blocked_ku"],
        "membership_final": ap["membership"], "certificate_final": ap["certificate"], "budget_cap_final": ap["budget_cap"],
        "watermarks": state["planes"]["ib1"]["watermarks"], "revocations": state["planes"]["ib1"]["revocations"],
        "admits": state["counters"]["admits"], "permits": state["counters"]["permits"], "refused_at_floor": state["counters"]["refused_floor"], "refused_by_bundle": state["counters"]["refused_bundle"],
        "by_rule": dict(sorted(state["counters"]["by_rule"].items())), "effects": state["counters"]["effects"], "peer_sends": state["counters"]["sends"], "beacons": state["counters"]["beacons"],
        "peer_adds_nothing": {"checked": len(pa), "held": sum(1 for e in pa if e["holds"])},
        "invariant_failures": state["counters"]["invariant_failures"],
        "vehicles_final": {v: {"alive": V["alive"], "mode": V["mode"], "sorties": V["sorties"], "fuel_pct": V["fuel_pct"], "chain_len": V["chain_len"]} for v, V in state["vehicles"].items()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", default=str(HERE / "out/trace.jsonl.gz"))
    ap.add_argument("--reeval", choices=["rego", "wasm"])
    ap.add_argument("--at", type=int)
    ap.add_argument("--timeline", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--admits")
    ap.add_argument("--from", dest="frm", type=int, default=0)
    ap.add_argument("--to", type=int, default=10**9)
    ap.add_argument("--explain", type=int)
    a = ap.parse_args()
    header, events = read_trace(a.trace)
    if a.timeline:
        return timeline(events)
    if a.explain:
        ev = next(e for e in events if e["seq"] == a.explain)
        return print(json.dumps(ev, indent=2, ensure_ascii=False))
    if a.admits:
        for ev in events:
            if ev["kind"] == "admit" and ev.get("by") in (f"gov:{a.admits}", "plane:ap1") and a.frm <= (ev["tick"] or 0) <= a.to:
                if ev["by"] == "plane:ap1" and ev["input"]["facts"]["vehicle"] != a.admits:
                    continue
                reasons = [v for r in ev.get("evals", []) for v in r.get("violations", [])] or ([ev["floor"]] if ev.get("floor") else [])
                print(f"#{ev['seq']:<6} {hhmm(ev['tick'])} t{ev['tick']:<5} {ev['decision']:5} {ev['what']:24} {'; '.join(reasons)}")
        return None
    if a.at is not None:
        state, errors, _ = rebuild(header, events, stop_at=a.at)
        if errors:
            print("\n".join(errors))
        p = state["planes"]["ap1"]
        print(f"{hhmm(a.at)} tick {a.at} · mesh {state['mesh']['status']} · members {len(p['membership'])}, cert {p['certificate']} · leases {p['budget_spent']}/{p['budget_cap']} · outstanding {p['outstanding']} · link above {'up' if state['planes']['ib1']['link_up'] else 'CUT'}")
        for v, V in state["vehicles"].items():
            L = V["lease"]
            print(f"  {v} {'alive' if V['alive'] else 'DEAD '} {V['mode']:9} ({V['pos']['e']:8.0f},{V['pos']['n']:8.0f},{V['pos']['alt_agl_m']:5.0f}) fuel {V['fuel_pct']:5.1f}%  "
                  f"lease {(L['id'] + ' ' + str(L['used']) + '/' + str(L['count']) + ' to t' + str(L['ttl_end'])) if L else '-':20} {'ALONE' if V['alone'] else ''} sensor {(V['sensor'] or {}).get('tool', '-')}")
        return None
    state, errors, hashes = rebuild(header, events)
    if a.summary:
        return print(json.dumps(summary(header, events, state), indent=2))
    print(f"{len(events)} events; hash chain and {hashes} state hashes {'OK' if not errors else 'FAILED'}")
    for e in errors[:20]:
        print(" ", e)
    for p, want in header["config_sha256"].items():
        got = __import__("hashlib").sha256((CFG / p).read_bytes()).hexdigest()
        if got != want:
            print(f"  note: {p} has changed since this trace was recorded")
    bad = len(errors)
    if a.reeval:
        n, diffs = reevaluate(events, a.reeval)
        print(f"re-evaluated {n} bundle decisions with {a.reeval}: {diffs} differences")
        bad += diffs
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
