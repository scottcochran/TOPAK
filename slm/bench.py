#!/usr/bin/env python3
"""Step 5 (measure before you budget): time real training steps per preset, then turn the
measurement into wall-clock estimates.

    uv run bench.py                              # llama presets 1m…46m, 16k vocab
    uv run bench.py --family ssd --presets 10m 46m
    uv run bench.py --presets 46m --budgets 1e9 2.5e9

Each preset runs full optimizer steps (compiled forward and backward, AdamW update, bf16 compute
over fp32 master weights) on random tokens. No data is needed. It reports tokens/s, achieved
TFLOPS (training FLOPs per token × tokens/s) and peak memory, then the wall-clock for each token
budget: the Chinchilla 20 tokens per parameter by default, plus any `--budgets`.

The session's table assumed ~1.5 TFLOPS sustained on a base M4. Small models do not fill the
GPU, so the 1M smoke model's rate understates what the 46M model achieves. Measure the preset you
will run, not just the smoke test. Results go to runs/bench/<family>.json.
"""
from __future__ import annotations

import argparse
import platform
import subprocess
import time
from functools import partial

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_map

from common import RUNS, write_json
from model import PRESETS, ModelConfig, build, count_params, flops_per_token
from train import loss_fn


def chip() -> str:
    try:
        return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return platform.processor()


def bench(c: ModelConfig, micro_batch: int, steps: int, dtype) -> dict:
    model = build(c, 0)
    n = count_params(model)
    master = tree_map(lambda p: p.astype(mx.float32), model.parameters())
    model.update(tree_map(lambda p: p.astype(dtype), master))
    opt = optim.AdamW(learning_rate=1e-4, betas=[0.9, 0.95], weight_decay=0.1)
    opt.init(master)
    lg = nn.value_and_grad(model, loss_fn)
    state = [model.state]
    f = partial(mx.compile, inputs=state, outputs=state)(lambda x, y: lg(model, x, y))

    def step(x):
        nonlocal master
        loss, g = f(x[:, :-1], x[:, 1:])
        g, _ = optim.clip_grad_norm(tree_map(lambda t: t.astype(mx.float32), g), 1.0)
        master = opt.apply_gradients(g, master)
        model.update(tree_map(lambda p: p.astype(dtype), master))
        mx.eval(loss, master, opt.state, model.parameters())

    x = mx.random.randint(0, c.vocab_size, (micro_batch, c.ctx + 1))
    for _ in range(3):
        step(x)
    mx.reset_peak_memory()
    t = time.time()
    for _ in range(steps):
        step(x)
    dt = (time.time() - t) / steps
    tps = micro_batch * c.ctx / dt
    fpt = flops_per_token(c, n["total"])
    return {"params": n["total"], "non_embedding": n["non_embedding"], "ctx": c.ctx, "micro_batch": micro_batch,
            "tok_per_s": round(tps), "tflops": round(tps * fpt / 1e12, 3), "flops_per_token": fpt,
            "peak_mem_gb": round(mx.get_peak_memory() / 1e9, 2)}


def human(seconds: float) -> str:
    if seconds < 3600:
        return f"{seconds / 60:.0f} min"
    if seconds < 3 * 86400:
        return f"{seconds / 3600:.1f} h"
    return f"{seconds / 86400:.1f} days"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family", choices=["llama", "ssd"], default="llama")
    ap.add_argument("--presets", nargs="+", default=["1m", "10m", "30m", "46m"], choices=list(PRESETS))
    ap.add_argument("--vocab", type=int, default=16384)
    ap.add_argument("--micro-batch", type=int, default=16)
    ap.add_argument("--steps", type=int, default=10)
    ap.add_argument("--dtype", choices=["bfloat16", "float32"], default="bfloat16")
    ap.add_argument("--budgets", nargs="*", type=float, default=[], help="extra token budgets, e.g. 1e9")
    a = ap.parse_args()

    dtype = {"bfloat16": mx.bfloat16, "float32": mx.float32}[a.dtype]
    rows = []
    print(f"{chip()} · MLX {mx.__version__} · {a.family} · {a.dtype} · vocab {a.vocab} · micro-batch {a.micro_batch}")
    print(f"{'preset':>6} {'params':>8} {'ctx':>5} {'tok/s':>9} {'TFLOPS':>7} {'mem GB':>7}   wall-clock for budget")
    for p in a.presets:
        c = ModelConfig.from_preset(p, family=a.family, vocab_size=a.vocab)
        r = bench(c, a.micro_batch, a.steps, dtype)
        budgets = [20 * r["params"]] + [int(b) for b in a.budgets]
        r["estimates"] = [{"tokens": b, "seconds": round(b / r["tok_per_s"])} for b in budgets]
        est = "  ".join(f"{b / 1e6:,.0f}M tok → {human(b / r['tok_per_s'])}" for b in budgets)
        print(f"{p:>6} {r['params'] / 1e6:7.1f}M {c.ctx:5d} {r['tok_per_s']:9,d} {r['tflops']:7.2f} {r['peak_mem_gb']:7.2f}   {est}")
        rows.append({"preset": p, **r})
    write_json(RUNS / "bench" / f"{a.family}.json",
               {"chip": chip(), "mlx": mx.__version__, "family": a.family, "dtype": a.dtype, "vocab": a.vocab,
                "rows": rows})
    print("first budget per row is Chinchilla-optimal (20 tokens/parameter). Optimizer steps included;"
          " evaluation and checkpoint time are not.")


if __name__ == "__main__":
    main()
