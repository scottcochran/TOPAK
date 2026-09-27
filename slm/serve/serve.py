#!/usr/bin/env python3
"""Inference for a trained checkpoint, inside a locked-down container.

The container has no network, a read-only root and no capabilities, and runs as a non-root
user. The only way in or out is stdio:

  default          MCP over stdio (JSON-RPC 2.0, one message per line): tools `generate` and
                   `model_info`, just enough surface for an MCP client (initialize, tools/list,
                   tools/call, ping)
  --prompt TEXT    one-shot generation to stdout, for smoke tests

The bundle is three read-only files under $SLM_BUNDLE (default /model): `model.json` and
`model.safetensors` from a train.py output directory, and the `tokenizer.json` the run was
tokenized with. `model.json` records the SHA-256 of the other two (`weights`, `tokenizer`), and
both are checked before anything is served. Set SLM_MODEL_SHA256 to the digest of `model.json`
to pin the bundle itself; a mismatch refuses to start.

MLX runs on its CPU backend here: a Linux container cannot reach the Mac's Metal GPU. That is
fine for inference at 1–125M parameters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # model.py; `python -I` omits it

import mlx.core as mx  # noqa: E402
from mlx.utils import tree_unflatten  # noqa: E402

from model import LM, ModelConfig  # noqa: E402

BUNDLE = pathlib.Path(os.environ.get("SLM_BUNDLE", "/model"))
MAX_NEW = int(os.environ.get("SLM_MAX_NEW", "512"))
MAX_PROMPT_CHARS = int(os.environ.get("SLM_MAX_PROMPT_CHARS", "16384"))
EOT = "<|endoftext|>"


def say(*a):
    print(*a, file=sys.stderr, flush=True)


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


class Refused(Exception):
    pass


def load_bundle(root: pathlib.Path):
    from tokenizers import Tokenizer

    paths = {k: root / k for k in ("model.json", "model.safetensors", "tokenizer.json")}
    for p in paths.values():
        if not p.is_file():
            raise Refused(f"missing {p}")
    pinned = os.environ.get("SLM_MODEL_SHA256", "").strip().lower()
    got = sha256_file(paths["model.json"])
    if pinned and got != pinned:
        raise Refused(f"model.json digest {got[:16]} is not the pinned {pinned[:16]}")
    desc = json.loads(paths["model.json"].read_text())
    for field, key in (("weights", "model.safetensors"), ("tokenizer", "tokenizer.json")):
        want, have = desc.get(field), sha256_file(paths[key])
        if want != have:
            raise Refused(f"{key} digest {have[:16]} is not model.json's {field} {str(want)[:16]}")
    model = LM(ModelConfig(**desc["model_config"]))
    model.update(tree_unflatten(list(mx.load(str(paths["model.safetensors"])).items())))
    mx.eval(model.parameters())
    tok = Tokenizer.from_file(str(paths["tokenizer.json"]))
    if tok.get_vocab_size() != model.config.vocab_size:
        raise Refused(f"tokenizer vocab {tok.get_vocab_size()} is not the model's {model.config.vocab_size}")
    info = {
        "model_json_sha256": got,
        "weights_sha256": desc["weights"],
        "tokenizer_sha256": desc["tokenizer"],
        "family": desc.get("family_tag"),
        "params": desc.get("params"),
        "root": desc.get("root"),
        "ctx": model.config.ctx,
        "max_new_tokens": MAX_NEW,
    }
    return model, tok, info


def generate(model: LM, ids: list[int], n: int, temperature: float, top_k: int, eot: int | None) -> list[int]:
    """sample.py's loop, stopping before the end-of-text token. It recomputes the window each step
    (no KV cache); at this size that is cheap."""
    ctx = model.config.ctx
    out = list(ids)
    for _ in range(n):
        logits = model(mx.array([out[-ctx:]]))[0, -1].astype(mx.float32)
        if temperature <= 0:
            nxt = int(mx.argmax(logits).item())
        else:
            logits = logits / temperature
            if top_k:
                kth = mx.sort(logits)[-top_k]
                logits = mx.where(logits < kth, -mx.inf, logits)
            nxt = int(mx.random.categorical(logits).item())
        if eot is not None and nxt == eot:
            break
        out.append(nxt)
    return out[len(ids):]


def _int(args, key, default, lo, hi):
    v = args.get(key, default)
    if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
        raise ValueError(f"{key} must be an integer in [{lo}, {hi}]")
    return v


def _num(args, key, default, lo, hi):
    v = args.get(key, default)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
        raise ValueError(f"{key} must be a number in [{lo}, {hi}]")
    return float(v)


class Server:
    def __init__(self, model, tok, info):
        self.model, self.tok, self.info = model, tok, info
        self.eot = tok.token_to_id(EOT)
        vocab = model.config.vocab_size
        self.tools = {
            "generate": ("Continue a text prompt with the sandboxed small language model.", {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "maxLength": MAX_PROMPT_CHARS,
                               "description": "text to continue; empty starts a fresh document"},
                    "max_new_tokens": {"type": "integer", "minimum": 1, "maximum": MAX_NEW, "default": 128},
                    "temperature": {"type": "number", "minimum": 0, "maximum": 2, "default": 0.8,
                                    "description": "0 is greedy"},
                    "top_k": {"type": "integer", "minimum": 0, "maximum": vocab, "default": 50,
                              "description": "0 disables top-k"},
                    "seed": {"type": "integer", "minimum": 0, "maximum": 2**32 - 1, "default": 0},
                },
                "required": ["prompt"],
                "additionalProperties": False,
            }),
            "model_info": ("Digests and shape of the loaded model bundle.",
                           {"type": "object", "properties": {}, "additionalProperties": False}),
        }

    def complete(self, args: dict) -> str:
        extra = set(args) - set(self.tools["generate"][1]["properties"])
        if extra:
            raise ValueError(f"unknown arguments {sorted(extra)}")
        prompt = args.get("prompt")
        if not isinstance(prompt, str) or len(prompt) > MAX_PROMPT_CHARS:
            raise ValueError(f"prompt must be a string of at most {MAX_PROMPT_CHARS} characters")
        n = _int(args, "max_new_tokens", 128, 1, MAX_NEW)
        temperature = _num(args, "temperature", 0.8, 0, 2)
        top_k = _int(args, "top_k", 50, 0, self.model.config.vocab_size)
        mx.random.seed(_int(args, "seed", 0, 0, 2**32 - 1))
        ids = self.tok.encode(prompt).ids if prompt else [self.eot]
        return self.tok.decode(generate(self.model, ids, n, temperature, top_k, self.eot))

    def call(self, name: str, args: dict) -> str:
        if name == "generate":
            return self.complete(args)
        if name == "model_info":
            return json.dumps(self.info)
        raise ValueError(f"unknown tool {name}")

    def serve(self):
        # A stray print from a library would corrupt the protocol, so fd 1 goes to stderr and
        # replies go to a private duplicate of the original stdout.
        proto = os.fdopen(os.dup(1), "w", buffering=1)
        os.dup2(2, 1)
        sys.stdout = sys.stderr

        def send(msg):
            proto.write(json.dumps(msg) + "\n")
            proto.flush()

        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
                mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
            except (json.JSONDecodeError, AttributeError):
                send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
                continue
            if mid is None:
                continue  # notifications
            if method == "initialize":
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "topak-slm-serve", "version": "0.1.0"}}})
            elif method == "tools/list":
                send({"jsonrpc": "2.0", "id": mid, "result": {"tools": [
                    {"name": n, "description": d, "inputSchema": s} for n, (d, s) in self.tools.items()]}})
            elif method == "tools/call":
                try:
                    text = self.call(params.get("name"), params.get("arguments") or {})
                    res = {"content": [{"type": "text", "text": text}], "isError": False}
                except ValueError as e:
                    res = {"content": [{"type": "text", "text": str(e)}], "isError": True}
                except Exception:
                    say(traceback.format_exc())
                    res = {"content": [{"type": "text", "text": "internal error"}], "isError": True}
                send({"jsonrpc": "2.0", "id": mid, "result": res})
            elif method == "ping":
                send({"jsonrpc": "2.0", "id": mid, "result": {}})
            else:
                send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"no method {method}"}})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", help="generate once to stdout instead of serving MCP")
    ap.add_argument("--max-new", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    try:
        server = Server(*load_bundle(BUNDLE))
    except Refused as e:
        say(f"topak-slm-serve: {e}; refusing")
        sys.exit(3)
    say(f"topak-slm-serve: {server.info['family']} {server.info['params']} "
        f"model.json {server.info['model_json_sha256'][:16]} on {mx.default_device()}")
    if a.prompt is None:
        server.serve()
        return
    try:
        text = server.complete({"prompt": a.prompt, "max_new_tokens": a.max_new, "temperature": a.temperature,
                                "top_k": a.top_k, "seed": a.seed})
    except ValueError as e:
        say(f"topak-slm-serve: {e}")
        sys.exit(2)
    print(a.prompt + text)


if __name__ == "__main__":
    main()
