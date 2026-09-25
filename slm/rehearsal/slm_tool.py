"""The SLM pipeline as downstream MCP tools, for the reference mechanism's `Invoke`.

Three tools, each taking one workspace-relative argument, `config`, the path of a JSON config the
principal drafted into the workspace:

  slm_tokenizer    train_tokenizer.train(config)
  slm_pretokenize  pretokenize.run(config)
  slm_pretrain     train.run(config)

Keeping every parameter in a drafted file, not in the tool inputs, means the log carries the
config as a `Draft` content digest, and the `Invoke` inputs digest is over a single path string.
No float is ever digested on both sides.

The reference pins a tool by SHA-256(executable ‖ input schema) (mechanism I13). The executable
is the generated wrapper from `pin_tool.py`. It embeds the digest of this file and of the
pipeline's code files, and `main` refuses to serve if they differ, so the pin covers the code the
wrapper imports. It does not cover the interpreter or the installed wheels (G4, ADR-0035 §7).

Protocol: MCP over stdio, JSON-RPC 2.0, one message per line, with just enough surface for the
reference's `rmcp` client (initialize, tools/list, tools/call, ping). Anything written to fd 1
by a library would corrupt the stream, so fd 1 is redirected to stderr and the protocol writes
to a private duplicate.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import traceback

HERE = pathlib.Path(__file__).resolve().parent
SLM = HERE.parent

SCHEMA = {
    "type": "object",
    "properties": {"config": {"type": "string", "description": "workspace-relative path of a JSON config"}},
    "required": ["config"],
    "additionalProperties": False,
}
TOOLS = {
    "slm_tokenizer": "Train a byte-level BPE tokenizer on workspace corpus shards.",
    "slm_pretokenize": "Tokenize workspace corpus shards into uint16 train/val token files.",
    "slm_pretrain": "Pre-train (or fine-tune) a small language model on workspace token files.",
}


def pinned_digest() -> str:
    sys.path.insert(0, str(SLM))
    from common import code_digest

    return hashlib.sha256((code_digest()["digest"] + hashlib.sha256((HERE / "slm_tool.py").read_bytes()).hexdigest())
                          .encode()).hexdigest()


def inside(path: str) -> pathlib.Path:
    p = pathlib.PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts or not path:
        raise ValueError(f"{path!r} is not workspace-relative")
    return pathlib.Path(path)


def check_config(cfg: dict):
    for k, v in cfg.items():
        if k in ("objects", "out", "tokenizer", "tokens", "init_from") and v is not None:
            inside(v)


def call(name: str, args: dict) -> dict:
    cfg_path = inside(args["config"])
    cfg = json.loads(cfg_path.read_text())
    check_config(cfg)
    if name == "slm_tokenizer":
        import train_tokenizer

        return train_tokenizer.train(cfg)
    if name == "slm_pretokenize":
        import pretokenize

        return pretokenize.run(cfg)
    if name == "slm_pretrain":
        import train

        return train.run(cfg, config_path=cfg_path)
    raise ValueError(f"unknown tool {name}")


def main(expected_digest: str):
    got = pinned_digest()
    if got != expected_digest:
        print(f"topak-slm-tool: code digest {got[:16]} is not the pinned {expected_digest[:16]}; refusing",
              file=sys.stderr)
        sys.exit(3)
    proto = os.fdopen(os.dup(1), "w", buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr

    def send(msg):
        proto.write(json.dumps(msg) + "\n")
        proto.flush()

    for line in sys.stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
        if mid is None:
            continue  # notifications
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "topak-slm", "version": "0.1.0"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": [
                {"name": n, "description": d, "inputSchema": SCHEMA} for n, d in TOOLS.items()]}})
        elif method == "tools/call":
            try:
                out = call(params["name"], params.get("arguments") or {})
                res = {"content": [{"type": "text", "text": json.dumps(out)}], "isError": False}
            except SystemExit as e:
                res = {"content": [{"type": "text", "text": f"exited: {e}"}], "isError": True}
            except Exception:
                res = {"content": [{"type": "text", "text": traceback.format_exc()[-2000:]}], "isError": True}
            send({"jsonrpc": "2.0", "id": mid, "result": res})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        else:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"no method {method}"}})
