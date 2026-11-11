#!/usr/bin/env python3
"""Parity of the compiled occupant with the trained model as slm/model.py runs it in MLX.

    slm/.venv/bin/python slm/occupant/parity.py --bundle <dir with model.json, model.safetensors,
        tokenizer.json> [--occupant slm/occupant/target/release/occupant] [--out results.txt]

Three checks, each against the same three bundle files:
  tokenizer  the Rust and Python `tokenizers` give identical ids for a fixed sample set
  logits     last-position logits agree within TOL for fixed prompts
  greedy     64 greedy tokens are identical for each prompt (serve.py's generate at temperature 0)

Exit 0 when all pass. Seeded sampling is not compared: the occupant's random stream is its own.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
SLM = HERE.parent
sys.path.insert(0, str(SLM))

import mlx.core as mx  # noqa: E402
from mlx.utils import tree_unflatten  # noqa: E402
from tokenizers import Tokenizer  # noqa: E402

from model import LM, ModelConfig  # noqa: E402

TOL = 1e-3
GREEDY = 64
SAMPLES = [
    "The history of the city",
    "Photosynthesis is the process by which",
    "In 1905, Albert Einstein published",
    "  leading spaces,\ttabs\tand\n\nblank lines\n",
    "Unicode: café, naïve, Zürich, 東京, emoji 🙂, and ‘quotes’ — dashes.",
    "Numbers 3.14159, 1,000,000 and dates 2026-11-11; code: def f(x): return x**2",
    "",
]
PROMPTS = SAMPLES[:3] + [SAMPLES[4], "Students should"]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def occ(binary: str, bundle: pathlib.Path, *args: str) -> dict:
    r = subprocess.run([binary, args[0], "--bundle", str(bundle), *args[1:]], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"occupant {args[0]} failed ({r.returncode}): {r.stderr}")
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=pathlib.Path)
    ap.add_argument("--occupant", default=str(HERE / "target/release/occupant"))
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args()

    desc = json.loads((a.bundle / "model.json").read_text())
    model = LM(ModelConfig(**desc["model_config"]))
    model.update(tree_unflatten(list(mx.load(str(a.bundle / "model.safetensors")).items())))
    mx.eval(model.parameters())
    tok = Tokenizer.from_file(str(a.bundle / "tokenizer.json"))
    eot = tok.token_to_id("<|endoftext|>")
    ctx = model.config.ctx

    lines = [
        f"# compiled occupant parity · {time.strftime('%Y.%m.%d %H:%M:%S %z')}",
        f"bundle model.json {sha(a.bundle / 'model.json')}",
        f"occupant binary   {sha(pathlib.Path(a.occupant))}",
        f"mlx {mx.__version__} (device {mx.default_device()}), tokenizers (python) {__import__('tokenizers').__version__}",
        "",
    ]
    ok = True

    lines.append("## tokenizer: identical ids")
    for s in SAMPLES:
        py = tok.encode(s).ids
        rs = occ(a.occupant, a.bundle, "encode", "--prompt", s)["ids"]
        same = py == rs
        ok &= same
        lines.append(f"  {'PASS' if same else 'FAIL'}  {len(py):3d} ids  {json.dumps(s)[:60]}")

    lines.append(f"## logits: max |Δ| at the last position < {TOL}")
    for p in PROMPTS:
        ids = tok.encode(p).ids or [eot]
        py = model(mx.array([ids]))[0, -1].astype(mx.float32)
        rs = mx.array(occ(a.occupant, a.bundle, "logits", "--ids", ",".join(map(str, ids)))["logits"])
        d = float(mx.max(mx.abs(py - rs)).item())
        same_top = int(mx.argmax(py).item()) == int(mx.argmax(rs).item())
        good = d < TOL and same_top
        ok &= good
        lines.append(f"  {'PASS' if good else 'FAIL'}  max|Δ| {d:.2e}  argmax equal {same_top}  {json.dumps(p)[:50]}")

    lines.append(f"## greedy: {GREEDY} tokens identical (serve.py's generate, temperature 0)")
    for p in PROMPTS:
        ids = tok.encode(p).ids or [eot]
        out = list(ids)
        for _ in range(GREEDY):
            nxt = int(mx.argmax(model(mx.array([out[-ctx:]]))[0, -1]).item())
            if nxt == eot:
                break
            out.append(nxt)
        py = out[len(ids):]
        r = occ(a.occupant, a.bundle, "generate", "--prompt", p, "--max-new", str(GREEDY), "--temperature", "0")
        same = r["prompt_ids"] == ids and r["ids"] == py
        ok &= same
        first = next((i for i, (x, y) in enumerate(zip(py, r["ids"])) if x != y), None)
        note = "" if same else f"  first difference at token {first}, lengths {len(py)}/{len(r['ids'])}"
        lines.append(f"  {'PASS' if same else 'FAIL'}  {len(py):3d} tokens  {json.dumps(p)[:50]}{note}")
        lines.append(f"        → {json.dumps(tok.decode(py))[:110]}")

    lines += ["", f"RESULT {'PASS' if ok else 'FAIL'}"]
    text = "\n".join(lines) + "\n"
    print(text, end="")
    if a.out:
        a.out.write_text(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
