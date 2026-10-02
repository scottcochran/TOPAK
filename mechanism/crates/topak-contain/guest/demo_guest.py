#!/usr/bin/env python3
"""The scripted occupant for a container (ADR-0036 §3): `topak-demo-guest`'s rung-1 protocol in
Python, so a Linux image can run it on any host. Standard library only; no network, no files but
the Persona bundle it is given.

    python3 demo_guest.py --model /model/model.json [--script draft,submit] [--exit]

It checks the weights against model.json and exits 3 before its identity line on a mismatch; it
holds no token and no key (rung 1: the launcher's bridge is the session).
"""
import hashlib
import json
import os
import sys


def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def digest_json(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    args = sys.argv[1:]
    model = args[args.index("--model") + 1]
    script = args[args.index("--script") + 1].split(",") if "--script" in args else []
    raw = open(model, "rb").read()
    m = json.loads(raw)
    weights = os.path.join(os.path.dirname(model), m.get("weights", "weights.bin"))
    try:
        ok = hashlib.sha256(open(weights, "rb").read()).hexdigest() == m.get("weights_sha256")
    except OSError:
        ok = False
    if not ok:
        print("the weights do not match model.json", file=sys.stderr)
        sys.exit(3)
    persona = hashlib.sha256(raw).hexdigest()
    send({"msg": "hello", "persona": persona, "family": m.get("family", "demo"),
          "params": m.get("params", 0), "root": "demo", "session_key": None})

    def next_response():
        for line in sys.stdin:
            h = json.loads(line)
            if h["msg"] == "attest":
                send({"msg": "evidence", "report_data": digest_json({"nonce": h["nonce"], "sessionKey": None})})
            elif h["msg"] == "granted":
                return {"granted": h["fence"]}
            elif h["msg"] == "response":
                return h["response"]
            elif h["msg"] == "shutdown":
                return None
        return None

    if next_response() is None:
        return
    for step in script:
        if step == "draft":
            op = {"op": "act", "action": {"kind": "Draft", "target": "notes.md",
                                          "content": f"drafted in a container under Persona {persona[:16]}\n"}}
        elif step == "submit":
            op = {"op": "submit_workspace"}
        else:
            sys.exit(2)
        send({"msg": "op", "op": op, "proof": None})
        r = next_response()
        if r is None:
            return
        print(f"{step}: {r}", file=sys.stderr)
    if "--exit" in args:
        return
    while next_response() is not None:
        pass


if __name__ == "__main__":
    main()
