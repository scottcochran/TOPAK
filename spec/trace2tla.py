#!/usr/bin/env python3
"""Turn a `topak-core` trace (`TOPAK_TRACE_DIR/<name>.jsonl`) into a TLA+ module that TLC
checks against `Mechanism.tla` (ADR-0045 T-0045-28, stage 1: trace validation).

Usage: trace2tla.py <trace.jsonl> [outdir]   → writes Trace_<name>.tla and Trace_<name>.cfg

Encoding (see `trace.rs`): {"$f": [[k, v], ...]} is a function, {"$s": [...]} a set, an array a
tuple, any other object a record. The module defines `TraceInitState` and `TraceSeq`, which the
cfg binds to Mechanism's constants.
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
    name = re.sub(r"[^A-Za-z0-9_]", "_", os.path.basename(src).rsplit(".", 1)[0])
    with open(src) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    if not lines or "init" not in lines[0]:
        sys.exit(f"{src}: first line must be the init projection")
    init = lines[0]["init"]
    steps = lines[1:]
    mod = f"Trace_{name}"
    body = [f"---- MODULE {mod} ----", "EXTENDS Mechanism", "", f"TraceInitState == {tla(init)}", ""]
    if steps:
        body.append("TraceSeq == <<")
        body.append(",\n".join(
            f"  [index |-> {s['index']}, entry |-> {tla(s['entry'])}, applied |-> {tla(s['applied'])}, state |-> {tla(s['state'])}]"
            for s in steps))
        body.append(">>")
    else:
        body.append("TraceSeq == <<>>")
    body.append("====")
    with open(os.path.join(outdir, mod + ".tla"), "w") as f:
        f.write("\n".join(body) + "\n")
    with open(os.path.join(outdir, mod + ".cfg"), "w") as f:
        f.write("SPECIFICATION TraceSpec\nINVARIANT TraceMatches\nCONSTANTS\n  InitState <- TraceInitState\n  Trace <- TraceSeq\n")
    print(f"{mod} {len(steps)}")


if __name__ == "__main__":
    main()
