#!/usr/bin/env python3
"""Live smoke test: three `topak node` processes over TCP, the operator CLI, and an MCP client
speaking JSON-RPC to `topak mcp` on stdio — the path a real agent takes.

Run `scripts/dev-init.sh [--kafka] [--opa]` first.

In the compose cluster (compose.cluster.yml) the replicas are services, so the script does not start them:
`docker compose -f compose.cluster.yml run --rm client` sets TOPAK_NODES_EXTERNAL=1, and TOPAK_DEV and
TOPAK_BIN_DIR to the image's paths."""
import json, os, subprocess, sys, time, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
DEV = pathlib.Path(os.environ.get("TOPAK_DEV") or HERE / "dev")
BIN = pathlib.Path(os.environ.get("TOPAK_BIN_DIR") or HERE / "target" / "debug") / "topak"
EXTERNAL = os.environ.get("TOPAK_NODES_EXTERNAL") == "1"

def op(node, req, quiet=False):
    # `topak op` prints the reply and exits non-zero when the reply is a refusal: return it either way,
    # so a caller can read why.
    r = subprocess.run([BIN, "op", "--socket", DEV / f"run/n{node}/operator.sock", json.dumps(req)],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        if quiet:
            return None
        err = (r.stderr.strip().splitlines() or ["no output"])[0]
        sys.exit(f"topak op on replica {node} gave no reply (exit {r.returncode}): {err}")

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
    nodes = []
    if not EXTERNAL:
        for n in (1, 2, 3):
            (DEV / f"run/n{n}").mkdir(parents=True, exist_ok=True)
        logs = [open(DEV / f"run/n{n}.log", "w") for n in (1, 2, 3)]
        nodes = [subprocess.Popen([BIN, "node", "--config", DEV / f"n{n}.json"], stdout=logs[n - 1],
                                  stderr=logs[n - 1]) for n in (1, 2, 3)]
    try:
        # Wait until every replica answers and one leads. A socket file left by an earlier run is not a
        # listening replica, so ask each one and do not look for the file.
        for _ in range(150):
            up = [op(n, {"op": "status"}, quiet=True) for n in (1, 2, 3)]
            if all(up) and any(s.get("leader") for s in up):
                break
            time.sleep(0.1)
        else:
            where = "docker compose -f compose.cluster.yml logs" if EXTERNAL else f"{DEV}/run/n*.log"
            sys.exit(f"the replicas did not come up with a leader in 15 s: see {where}")
        params = json.loads((DEV / "params.json").read_text())
        env = DEV / ".env" if (DEV / ".env").exists() else HERE / ".env"
        bundle = env.read_text().strip().split("=", 1)[1]
        obj = params["corpus"][0]
        tool, digest = params["build_tools"][0].split("@")

        # The replicas keep their logs under dev/run/, and a seat's round number is never reused, so a run
        # after the first takes the next round the seat has not had. `dev-init.sh` starts again from round 1.
        for rnd in range(1, 1000):
            g = op(1, {"op": "grant", "principal": "agent-a1", "seat": "a1", "persona": "00" * 32,
                       "bundle": bundle, "confinement": {"digest": "00" * 32, "rung": 0},
                       "alphabet": ["Read", "Draft", "Invoke", "Emit", "Submit"], "ttl_ms": 120000,
                       "round": rnd, "role": "author"})
            if g.get("ok") or "round numbers are not reused" not in json.dumps(g):
                break
        assert g.get("ok"), g
        why = "; ".join(map(str, g.get("because") or [])) or "no reason given"
        print(f"grant a1: round {rnd}, fence {g['fence']}, contained={g['contained']} ({why})")

        m = Mcp(1, g["token"])
        tools = [t["name"] for t in m.rpc("tools/list", {})["result"]["tools"]]
        print(f"MCP tools offered: {tools}")
        show("read(corpus object)", m.call("read", {"object": obj}))
        show("read(object outside the corpus root)", m.call("read", {"object": "ab" * 32}))
        # The round is in the draft so that each run submits an artifact no earlier run submitted.
        show("draft(spec/Lease.tla)", m.call("draft", {"target": "spec/Lease.tla",
                                                       "content": f"VARIABLES lease\n\\* smoke round {rnd}\n"}))
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
