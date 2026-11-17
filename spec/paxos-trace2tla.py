#!/usr/bin/env python3
"""Turn a `topak-paxos` simulation trace (`TOPAK_TRACE_DIR/<name>.jsonl`, written by
`mechanism/crates/topak-paxos/tests/sim.rs`) into a TLA+ module that TLC checks against
`PaxosTrace.tla`: trace validation of the replica against `Paxos.tla`.

Usage: paxos-trace2tla.py <trace.jsonl> [outdir] [Mut]   → writes Trace_<name>[_as_<Mut>].tla and .cfg

The first line of a trace is {"init": {"n": N, "mut": M}}: the number of replicas, and the module's
name for the mutation the code ran under. `Mut` defaults to that; passing "none" for a trace of
mutated code is how the replay is shown to fail when the code is not the model's.

Encoding (see sim.rs): {"$f": [[k, v], ...]} is a function, {"$s": [...]} a set, an array a tuple,
any other object a record. Prints `<module> <events> <Mut>`.
"""
import json
import os
import re
import sys


def tla(v):
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, list):
        return "<<" + ", ".join(tla(x) for x in v) + ">>"
    if isinstance(v, dict):
        if "$f" in v:
            pairs = v["$f"]
            if not pairs:
                return "[x \\in {} |-> x]"
            return "(" + " @@ ".join(f"({tla(k)} :> {tla(val)})" for k, val in pairs) + ")"
        if "$s" in v:
            return "{" + ", ".join(tla(x) for x in v["$s"]) + "}"
        if not v:
            raise ValueError("empty record has no TLA+ form")
        return "[" + ", ".join(f"{k} |-> {tla(val)}" for k, val in sorted(v.items())) + "]"
    raise TypeError(type(v))


def main():
    src = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src)) or "."
    with open(src) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    if not lines or "init" not in lines[0]:
        sys.exit(f"{src}: first line must be the init line")
    init = lines[0]["init"]
    events = lines[1:]
    mut = sys.argv[3] if len(sys.argv) > 3 else init["mut"]
    name = re.sub(r"[^A-Za-z0-9_]", "_", os.path.basename(src).rsplit(".", 1)[0])
    mod = f"Trace_{name}" + ("" if mut == init["mut"] else f"_as_{mut}")
    values = sorted({e["value"] for e in events if e["ev"] in ("hand", "fwd", "dup")})
    body = [f"---- MODULE {mod} ----", "EXTENDS PaxosTrace", "", f"TraceValues == {tla({'$s': values})}", ""]
    if events:
        body.append("TraceSeq == <<")
        body.append(",\n".join("  " + tla(e) for e in events))
        body.append(">>")
    else:
        body.append("TraceSeq == << >>")
    body.append("====")
    with open(os.path.join(outdir, mod + ".tla"), "w") as f:
        f.write("\n".join(body) + "\n")
    with open(os.path.join(outdir, mod + ".cfg"), "w") as f:
        f.write(
            "SPECIFICATION TraceSpec\n"
            "INVARIANT TraceReceivable\nINVARIANT TraceStateMatches\nINVARIANT TraceSendsMatch\n"
            "INVARIANT TypeOK\nINVARIANT OneValuePerBallot\nINVARIANT ChosenUnique\nINVARIANT Agreement\n"
            "INVARIANT LearnerSound\nINVARIANT OnlyHanded\nINVARIANT NoAmplification\n"
            "CONSTANTS\n"
            f"  Mut = \"{mut}\"\n  N = {init['n']}\n  Values <- TraceValues\n  Trace <- TraceSeq\n"
            "  Electors = {}\n  Beaters = {}\n  Hosts = {}\n  Crashers = {}\n"
            "  MaxRound = 0\n  MaxHand = 0\n  MaxDup = 0\n  MaxCrash = 0\n"
        )
    print(f"{mod} {len(events)} {mut}")


if __name__ == "__main__":
    main()
