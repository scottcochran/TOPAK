#!/usr/bin/env python3
"""After changing the kernel: does the recon-fleet-7 example still make the decisions the frozen run made?

    regress.py NEW_TRACE [--baseline derived/recon-fleet-7-simulation-2026.11.10/out/trace.jsonl.gz]

Compares every admit (tick, who, what, stage, decision, the rules that refused it) and every lease grant
against the frozen trace. Ordering inside one tick is not compared, because nothing depends on it.
Exits 1 on any difference.
"""
import collections
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from topak_sim.trace import read_trace  # noqa: E402


def rules(ev):
    out = sorted(v for r in ev.get("evals", []) for v in r.get("violations", []))
    fl = ev.get("floor")
    if ev.get("stage") == "floor":
        out.append(fl if isinstance(fl, str) else fl.get("rule"))
    return tuple(out)


def admits(events):
    return collections.Counter((e["tick"], e["by"], e["what"], e["stage"], e["decision"], rules(e)) for e in events if e["kind"] == "admit")


def grants(events):
    return collections.Counter((e["tick"], e.get("body", e.get("vehicle")), e["node"], e["via"], e["count"], e["ttl_end"], e["certificate"], e["outstanding"]) for e in events if e["kind"] == "lease_grant")


def main():
    args = sys.argv[1:]
    base = "derived/recon-fleet-7-simulation-2026.11.10/out/trace.jsonl.gz"
    if "--baseline" in args:
        i = args.index("--baseline")
        base = args[i + 1]
        del args[i:i + 2]
    _, new = read_trace(args[0])
    _, old = read_trace(base)
    bad = 0
    for name, f in (("admits", admits), ("lease grants", grants)):
        a, b = f(old), f(new)
        only_old, only_new = a - b, b - a
        print(f"{name}: baseline {sum(a.values())}, new {sum(b.values())}, only in baseline {sum(only_old.values())}, only in new {sum(only_new.values())}")
        for k in sorted(only_old, key=str)[:15]:
            print("  baseline:", k)
        for k in sorted(only_new, key=str)[:15]:
            print("  new:     ", k)
        bad += sum(only_old.values()) + sum(only_new.values())
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
