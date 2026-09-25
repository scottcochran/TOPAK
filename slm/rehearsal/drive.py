#!/usr/bin/env python3
"""Run one lineage through the reference mechanism as a Build round, then project its record.

    uv run rehearsal/drive.py --name pg --family ssd --minutes 5
    uv run rehearsal/drive.py --name pg --family ssd --minutes 5 --tamper omit-object

The driver plays the author seat, speaking MCP to `topak mcp` as an agent would (as
mechanism/scripts/smoke.py does). One round, seat a1, rung 0:

  Read every corpus object              → Draft it to corpus/<digest>.jsonl   (a byte-copy)
  Draft config/tokenizer.json           → Invoke slm_tokenizer
  Draft config/pretokenize.json         → Invoke slm_pretokenize
  Draft config/pretrain.json            → Invoke slm_pretrain   (a ~1M-parameter model)
  Submit                                  (the artifact is the workspace digest)

Then it stops the replicas, writes the author's manifest.json from what the tools returned into
rehearsal/run/<name>/result-<honest|tamper>/, and runs lineage/project.py against replica 2's
archive. Replica 1 decided every action, so the projection is not taken from the replica that
ran the effects. The workspace itself exists only
on replica 1 (mechanism G9), so the projector reads it there and checks it against the
submitted digest.

`--tamper` makes the author's manifest lie, to show the cross-check produce a Contested lineage:
  omit-object   claim one fewer corpus object than was read
  seed          claim a different seed
  inject        also Draft a non-corpus text into corpus/ and leave it out of the manifest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
SLM = HERE.parent
sys.path.insert(0, str(SLM))
from common import load_json, write_json  # noqa: E402


class Mcp:
    def __init__(self, topak, sock, token):
        self.p = subprocess.Popen([topak, "mcp", "--socket", sock, "--token", token, "--domain", "build"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "slm-rehearsal", "version": "0"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def rpc(self, method, params):
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("topak mcp closed its stdout")
            m = json.loads(line)
            if m.get("id") == self.n:
                return m

    def call(self, name, args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        if "error" in r:
            return False, r["error"]
        res = r["result"]
        return not res.get("isError", False), json.loads(res["content"][0]["text"])

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


def must(label, ok_detail, log):
    ok, d = ok_detail
    log.append({"action": label, "admitted": ok, "detail": d if label.startswith(("invoke", "submit")) else
                {k: d.get(k) for k in ("decision", "slot", "floor", "reason") if isinstance(d, dict)}})
    tag = "ADMIT" if ok else "DENY "
    print(f"  {tag} {label:<48} slot {d.get('slot') if isinstance(d, dict) else '-'}")
    if not ok:
        raise SystemExit(f"{label}: {json.dumps(d)[:600]}")
    return d


def tool_result(d: dict) -> dict:
    """The downstream tool's JSON result, out of the mechanism's admit detail."""
    r = d["result"]
    if r.get("isError"):
        raise SystemExit(f"tool error: {r['content'][0]['text'][-1500:]}")
    return json.loads(r["content"][0]["text"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--lineage", help="label for the record (default R-<name>)")
    ap.add_argument("--family", choices=["llama", "ssd"], default="llama")
    ap.add_argument("--preset", default="1m")
    ap.add_argument("--vocab", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--minutes", type=float, default=10.0, help="pre-training wall-clock budget")
    ap.add_argument("--ttl-min", type=int, default=180, help="lease TTL; must outlast the whole round")
    ap.add_argument("--tamper", choices=["omit-object", "seed", "inject"])
    a = ap.parse_args()

    root = HERE / "run" / a.name
    cl = load_json(root / "cluster.json")
    topak = cl["topak"]
    lineage = a.lineage or f"R-{a.name}"
    out = root / f"result-{a.tamper or 'honest'}"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    # Each rehearsal is one round on a fresh log: seat a1, round 1. Replica state from an earlier
    # run is discarded (round numbers are never reused per seat, I16).
    for i in (1, 2, 3):
        shutil.rmtree(root / f"run/n{i}", ignore_errors=True)
        (root / f"run/n{i}").mkdir(parents=True)

    def op(node, req):
        r = subprocess.run([topak, "op", "--socket", root / f"run/n{node}/operator.sock", json.dumps(req)],
                           capture_output=True, text=True, check=True)
        return json.loads(r.stdout)

    logs = [open(root / f"run/n{i}.log", "w") for i in (1, 2, 3)]
    nodes = [subprocess.Popen([topak, "node", "--config", root / f"n{i}.json"], stdout=logs[i - 1],
                              stderr=logs[i - 1]) for i in (1, 2, 3)]
    transcript: list = []
    try:
        for _ in range(100):
            if all((root / f"run/n{i}/operator.sock").exists() for i in (1, 2, 3)):
                break
            time.sleep(0.1)
        time.sleep(1.5)  # leader election

        g = op(1, {"op": "grant", "principal": "agent-a1", "seat": "a1", "persona": "00" * 32,
                   "bundle": cl["bundle"], "confinement": {"digest": "00" * 32, "rung": 0},
                   "alphabet": ["Read", "Draft", "Invoke", "Submit"], "ttl_ms": a.ttl_min * 60_000,
                   "round": 1, "role": "author"})
        if not g.get("ok"):
            raise SystemExit(f"grant refused: {g}")
        print(f"grant a1 round 1: fence {g['fence']}, ttl {a.ttl_min} min, contained={g['contained']}")
        m = Mcp(topak, root / "run/n1/agent.sock", g["token"])

        print("round:")
        read = []
        for d in cl["objects"]:
            r = must(f"read {d[:16]}", m.call("read", {"object": d}), transcript)
            content = r["result"]["content"]
            w = must(f"draft corpus/{d[:16]}….jsonl", m.call("draft", {"target": f"corpus/{d}.jsonl",
                                                                         "content": content}), transcript)
            assert w["result"]["digest"] == d, "the drafted copy is not byte-identical to the object"
            read.append(d)
        injected = None
        if a.tamper == "inject":
            text = json.dumps({"id": "injected", "text": "Text the author wrote into the corpus directory. " * 40}) + "\n"
            w = must("draft corpus/injected.jsonl (tamper)", m.call("draft", {"target": "corpus/injected.jsonl",
                                                                              "content": text}), transcript)
            injected = w["result"]["digest"]

        cfgs = {
            "tokenizer": {"objects": "corpus", "out": "tokenizer", "vocab_size": a.vocab, "sample_bytes": 50_000_000},
            "pretokenize": {"objects": "corpus", "tokenizer": "tokenizer/tokenizer.json", "out": "tokens",
                            "val_permille": 20},
            "pretrain": {"tokens": "tokens", "out": "ckpt", "seed": a.seed,
                         "model": {"family": a.family, "preset": a.preset}, "max_minutes": a.minutes,
                         "tokens_per_step": 32768, "eval_every": 100, "log_every": 50, "ckpt_minutes": 60},
        }
        results = {}
        for step, tool in (("tokenizer", "slm_tokenizer"), ("pretokenize", "slm_pretokenize"),
                           ("pretrain", "slm_pretrain")):
            text = json.dumps(cfgs[step], indent=2, sort_keys=True) + "\n"
            must(f"draft config/{step}.json", m.call("draft", {"target": f"config/{step}.json", "content": text}),
                 transcript)
            name, digest = cl["tools"][tool].split("@")
            t0 = time.time()
            d = must(f"invoke {tool}", m.call("invoke", {"tool": name, "digest": digest,
                                                        "inputs": {"config": f"config/{step}.json"}}), transcript)
            results[step] = tool_result(d)
            results[step]["_config_digest"] = hashlib.sha256(text.encode()).hexdigest()
            print(f"        {tool} took {time.time() - t0:.0f}s")
        s = must("submit", m.call("submit", {}), transcript)
        artifact = s["result"]["submitted"]
        print(f"submitted artifact {artifact}")
        m.close()
        time.sleep(0.5)
        status = op(2, {"op": "status"})
    finally:
        for p in nodes:
            p.terminate()
        for p in nodes:
            p.wait(timeout=10)
    write_json(out / "transcript.json", {"lineage": lineage, "actions": transcript, "status_n2": status})

    # The author's manifest, from what the author saw. Under --tamper, it lies.
    corpus = load_json(pathlib.Path(cl["corpus"]) / "corpus.json")
    sizes = {o["digest"]: o["bytes"] for o in corpus["objects"]}
    claimed = list(read)
    if a.tamper == "omit-object":
        claimed = claimed[:-1]
    pre = results["pretrain"]
    manifest = {
        "schema": "topak.slm.manifest/0",
        "lineage": lineage,
        "authored": {"by": "agent-a1", "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
        "corpus": [{"id": corpus["id"], "objects": [{"digest": d, "bytes": sizes[d]} for d in claimed],
                    "declaration": corpus["declaration"]}],
        "tokenizer": {"digest": results["tokenizer"]["digest"], "vocab_size": results["tokenizer"]["vocab_size"]},
        "tools": cl["tools"],
        "code": {"pin": cl["code_pin"]},
        "config": {"digest": results["pretrain"]["_config_digest"], "content": cfgs["pretrain"]},
        "seed": a.seed + (1 if a.tamper == "seed" else 0),
        "family": pre["family_tag"],
        "model": {"root": pre["root"], "weights": pre["weights"], "params": pre["params"],
                  "final_val_loss": pre["final_val_loss"], "steps": pre["steps"]},
        "artifact": artifact,
        "tamper": a.tamper,
    }
    write_json(out / "manifest.json", manifest)
    print(f"manifest {out / 'manifest.json'}" + (f"  (tampered: {a.tamper})" if a.tamper else ""))

    rc = subprocess.run([sys.executable, str(SLM / "lineage" / "project.py"),
                         "--archive", root / "run/n2/archive.jsonl", "--params", root / "params.json",
                         "--corpus-json", pathlib.Path(cl["corpus"]) / "corpus.json",
                         "--workspaces", root / "run/n1/workspaces", "--seat", "a1", "--lineage", lineage,
                         "--manifest", out / "manifest.json", "--out", out]).returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()
