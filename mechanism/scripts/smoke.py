#!/usr/bin/env python3
"""Live smoke test: three `topak node` processes over TCP, the operator CLI, and an MCP client
speaking JSON-RPC to `topak mcp` on stdio — the path a real agent takes.

Run `scripts/dev-init.sh [--kafka] [--opa]` first."""
import json, os, subprocess, sys, time, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
DEV, BIN = HERE / "dev", HERE / "target" / "debug" / "topak"

def op(node, req):
    out = subprocess.run([BIN, "op", "--socket", DEV / f"run/n{node}/operator.sock", json.dumps(req)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)

class Mcp:
    def __init__(self, node, token, domain="build"):
        self.p = subprocess.Popen([BIN, "mcp", "--socket", DEV / f"run/n{node}/agent.sock", "--token", token,
                                   "--domain", domain], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "smoke", "version": "0"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n"); self.p.stdin.flush()

    def rpc(self, method, params):
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            m = json.loads(self.p.stdout.readline())
            if m.get("id") == self.n:
                return m

    def call(self, name, args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        if "error" in r:
            return False, r["error"]
        res = r["result"]
        return not res.get("isError", False), json.loads(res["content"][0]["text"])

    def close(self):
        self.p.stdin.close(); self.p.wait(timeout=5)

def show(label, ok_detail):
    ok, d = ok_detail
    why = d.get("floor") if ok else d.get("reason", d)
    print(f"  {'ADMIT' if ok else 'DENY '}  {label:<44} {json.dumps(why)[:110]}")
    return ok, d

def main():
    for n in (1, 2, 3):
        (DEV / f"run/n{n}").mkdir(parents=True, exist_ok=True)
    logs = [open(DEV / f"run/n{n}.log", "w") for n in (1, 2, 3)]
    nodes = [subprocess.Popen([BIN, "node", "--config", DEV / f"n{n}.json"], stdout=logs[n - 1], stderr=logs[n - 1])
             for n in (1, 2, 3)]
    try:
        for _ in range(100):
            if all((DEV / f"run/n{n}/operator.sock").exists() for n in (1, 2, 3)):
                break
            time.sleep(0.1)
        time.sleep(1.0)  # leader election
        params = json.loads((DEV / "params.json").read_text())
        bundle = open(HERE / ".env").read().strip().split("=", 1)[1]
        obj = params["corpus"][0]
        tool, digest = params["build_tools"][0].split("@")

        g = op(1, {"op": "grant", "principal": "agent-a1", "seat": "a1", "persona": "00" * 32,
                   "bundle": bundle, "confinement": {"digest": "00" * 32, "rung": 0},
                   "alphabet": ["Read", "Draft", "Invoke", "Emit", "Submit"], "ttl_ms": 120000,
                   "round": 1, "role": "author"})
        assert g["ok"], g
        print(f"grant a1: fence {g['fence']}, contained={g['contained']} ({g['note']})")

        m = Mcp(1, g["token"])
        tools = [t["name"] for t in m.rpc("tools/list", {})["result"]["tools"]]
        print(f"MCP tools offered: {tools}")
        show("read(corpus object)", m.call("read", {"object": obj}))
        show("read(object outside the corpus root)", m.call("read", {"object": "ab" * 32}))
        show("draft(spec/Lease.tla)", m.call("draft", {"target": "spec/Lease.tla", "content": "VARIABLES lease\n"}))
        show("draft(../escape)", m.call("draft", {"target": "../escape", "content": "x"}))
        show("emit(record)", m.call("emit", {"record": {"note": "drafted"}}))
        show("invoke(wordcount) — bundle has no schema", m.call("invoke", {"tool": tool, "digest": digest,
                                                             "inputs": {"path": "spec/Lease.tla"}}))
        show("submit(workspace)", m.call("submit", {}))
        show("emit after submit", m.call("emit", {"record": {"late": True}}))
        m.close()

        r = op(2, {"op": "fence_epoch", "reason": "smoke", "attribution": "smoke.py"})
        print(f"fence_epoch via replica 2: slot {r.get('slot')}, {r.get('applied')}")
        time.sleep(0.3)
        for n in (1, 2, 3):
            s = op(n, {"op": "status"})
            print(f"replica {n}: leader={s['leader']} last_applied={s['last_applied']} epoch={s['epoch']} "
                  f"candidates={len(s['candidates'])} live={len(s['live_leases'])}")
    finally:
        for p in nodes:
            p.terminate()
        for p in nodes:
            p.wait(timeout=5)

if __name__ == "__main__":
    sys.exit(main())
