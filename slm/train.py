#!/usr/bin/env python3
"""Steps 5–7: pre-train (or fine-tune) a model on pre-tokenized data, resumably.

    # smoke test: ~1M parameters for 10 minutes, then read tokens/s from metrics.jsonl
    uv run train.py --tokens runs/smoke/tokens --out runs/smoke/ckpt --preset 1m --minutes 10

    # a full run from a config file (see configs/)
    uv run train.py --config configs/L-A.json

    # E1's fine-tune case: start from another lineage's weights
    uv run train.py --config configs/L-A-prime.json      # "init_from": "runs/L-A/ckpt"

Defaults follow the session plan: AdamW (β 0.9/0.95), peak LR 6e-4, 1% linear warmup, cosine
decay to 10% of peak, weight decay 0.1 on matrices only, gradient clipping at 1.0, bf16 compute
over fp32 master weights, and about 0.25M tokens per optimizer step via gradient accumulation.

Operator behaviour:
- A resumable checkpoint (fp32 weights, optimizer state, step) is written every `ckpt_minutes`
  (default 30), on SIGINT/SIGTERM, and at the end. Re-running the same command resumes. Batches
  are a pure function of (seed, step), so a resumed run sees the data an unbroken one would.
- `init.safetensors` is the from-scratch initialisation, saved before step 1. Its digest is the
  lineage `root` in ADR-0035 §1.
- `metrics.jsonl` gets train loss, LR, gradient norm, tokens/s and achieved TFLOPS every
  `log_every` steps, and held-out loss every `eval_every` steps.
"""
from __future__ import annotations

import argparse
import math
import os
import pathlib
import shutil
import signal
import sys
import time
from functools import partial

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map, tree_unflatten

from common import JsonlLog, load_json, say, sha256_file, write_json
from model import ModelConfig, build, count_params, flops_per_token

DEFAULTS = {
    "seed": 1234,
    "model": {"family": "llama", "preset": "46m"},
    "tokens_budget": None,  # total training tokens; or set max_steps
    "max_steps": None,
    "tokens_per_step": 262144,
    "micro_batch": 16,
    "lr_peak": 6e-4,
    "lr_final_frac": 0.1,
    "warmup_frac": 0.01,
    "weight_decay": 0.1,
    "betas": [0.9, 0.95],
    "grad_clip": 1.0,
    "dtype": "bfloat16",
    "eval_every": 250,
    "eval_batches": 20,
    "log_every": 10,
    "ckpt_minutes": 30,
    "max_minutes": None,  # wall-clock stop per invocation; with no budget or max_steps the schedule is sized to fit it
    "init_from": None,  # a checkpoint directory (fine-tune): its model.safetensors and model.json
    "compile": True,
    "keep_resume": False,
}

DTYPES = {"bfloat16": mx.bfloat16, "float16": mx.float16, "float32": mx.float32}


def model_config(cfg: dict, vocab: int) -> ModelConfig:
    m = dict(cfg["model"])
    preset = m.pop("preset", None)
    m.setdefault("vocab_size", vocab)
    return ModelConfig.from_preset(preset, **m) if preset else ModelConfig(**m)


class Batches:
    """Random windows from a memory-mapped uint16 token file. Batch (step, micro) is drawn from
    a generator seeded by (seed, stream, step, micro): stateless, so resuming needs only the
    step. Streams keep training, evaluation and calibration draws apart."""

    TRAIN, EVAL, CALIBRATE = 0, 1, 2

    def __init__(self, path: pathlib.Path, ctx: int, micro_batch: int, seed: int):
        self.data = np.memmap(path, dtype=np.uint16, mode="r")
        self.ctx, self.mb, self.seed = ctx, micro_batch, seed
        if len(self.data) <= ctx + 1:
            raise ValueError(f"{path} has {len(self.data)} tokens, fewer than one window of {ctx + 1}")

    def get(self, step: int, micro: int, stream: int = TRAIN):
        rng = np.random.default_rng([self.seed, stream, step, micro])
        starts = rng.integers(0, len(self.data) - self.ctx - 1, self.mb)
        w = np.stack([self.data[s:s + self.ctx + 1] for s in starts]).astype(np.int32)
        return mx.array(w[:, :-1]), mx.array(w[:, 1:])


def loss_fn(model, x, y):
    logits = model(x).astype(mx.float32)
    return nn.losses.cross_entropy(logits, y, reduction="mean")


def make_optimizer(cfg: dict, total_steps: int):
    warm = max(1, int(total_steps * cfg["warmup_frac"]))
    peak = cfg["lr_peak"]
    sched = optim.join_schedules(
        [optim.linear_schedule(0.0, peak, warm),
         optim.cosine_decay(peak, max(1, total_steps - warm), end=peak * cfg["lr_final_frac"])],
        [warm],
    )
    betas = list(cfg["betas"])
    decayed = optim.AdamW(learning_rate=sched, betas=betas, weight_decay=cfg["weight_decay"])
    plain = optim.AdamW(learning_rate=sched, betas=betas, weight_decay=0.0)
    # Vectors (norm weights, dt_bias, A_log, D) take no weight decay.
    return optim.MultiOptimizer([plain, decayed], [lambda path, w: w.ndim < 2]), sched


def save_weights(path: pathlib.Path, params: dict):
    mx.save_safetensors(str(path), dict(tree_flatten(params)))


def load_weights(path: pathlib.Path) -> dict:
    return tree_unflatten(list(mx.load(str(path)).items()))


class Checkpoints:
    def __init__(self, out: pathlib.Path):
        self.dir = out / "resume"
        self.dir.mkdir(parents=True, exist_ok=True)

    def latest(self):
        f = self.dir / "LATEST"
        if f.exists():
            d = self.dir / f.read_text().strip()
            if (d / "state.json").exists():
                return d
        return None

    def save(self, step: int, master: dict, opt, state: dict):
        d = self.dir / f"step-{step:08d}"
        tmp = self.dir / f".tmp-{step:08d}"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        save_weights(tmp / "weights.safetensors", master)
        mx.save_safetensors(str(tmp / "optimizer.safetensors"), dict(tree_flatten(opt.state)))
        write_json(tmp / "state.json", state)
        shutil.rmtree(d, ignore_errors=True)
        os.replace(tmp, d)
        (self.dir / ".LATEST.tmp").write_text(d.name + "\n")
        os.replace(self.dir / ".LATEST.tmp", self.dir / "LATEST")
        for old in sorted(p for p in self.dir.glob("step-*") if p != d)[:-1]:
            shutil.rmtree(old, ignore_errors=True)
        return d


def calibrate(micro, train: Batches, accum: int, minutes: float) -> int:
    """Size a time-boxed run: time a few forward/backward passes (after two untimed ones, which
    include compilation) and return the number of optimizer steps that fit in `minutes`,
    leaving 10% for evaluation and checkpoints."""
    for i in range(2):
        mx.eval(micro(*train.get(0, i, Batches.CALIBRATE)))
    t = time.time()
    n = 4
    for i in range(n):
        mx.eval(micro(*train.get(1, i, Batches.CALIBRATE)))
    per_step = (time.time() - t) / n * accum
    steps = max(10, int(minutes * 60 * 0.9 / per_step))
    say(f"calibrated: {per_step:.3f} s/step, {steps} steps fit in {minutes:g} min")
    return steps


def evaluate(model, val: Batches, n: int) -> float:
    losses = []
    for i in range(n):
        x, y = val.get(0, i, Batches.EVAL)  # a fixed set of windows, the same at every evaluation
        losses.append(loss_fn(model, x, y))
    return mx.mean(mx.stack(losses)).item()


def run(cfg: dict, base: pathlib.Path = pathlib.Path("."), config_path: pathlib.Path | None = None) -> dict:
    cfg = {**DEFAULTS, **cfg}
    tokens = base / cfg["tokens"]
    out = base / cfg["out"]
    out.mkdir(parents=True, exist_ok=True)
    tmeta = load_json(tokens / "meta.json")
    mcfg = model_config(cfg, tmeta["vocab_size"])
    dtype = DTYPES[cfg["dtype"]]
    config_digest = sha256_file(config_path) if config_path else None

    ctx, mb = mcfg.ctx, cfg["micro_batch"]
    accum = max(1, cfg["tokens_per_step"] // (mb * ctx))
    step_tokens = accum * mb * ctx
    ck = Checkpoints(out)
    resume = ck.latest()
    if resume is not None:
        total_steps = load_json(resume / "state.json")["total_steps"]
    elif cfg["max_steps"]:
        total_steps = int(cfg["max_steps"])
    elif cfg["tokens_budget"]:
        total_steps = max(1, int(cfg["tokens_budget"]) // step_tokens)
    elif cfg["max_minutes"]:
        total_steps = None  # sized below from a measured step time
    else:
        sys.exit("set tokens_budget, max_steps or max_minutes")

    # Model and master weights. `init.safetensors` is written once, before any update.
    model = build(mcfg, cfg["seed"])
    init = {"kind": "scratch", "seed": cfg["seed"]}
    if cfg["init_from"]:
        parent = base / cfg["init_from"]
        pm = load_json(parent / "model.json")
        if pm["model_config"] != mcfg.to_dict():
            sys.exit(f"init_from {parent}: model config differs from this run's")
        model.update(load_weights(parent / "model.safetensors"))
        init = {"kind": "parent", "weights": sha256_file(parent / "model.safetensors"), "root": pm["root"],
                "parent_model_json": sha256_file(parent / "model.json")}
    init_path = out / "init.safetensors"
    if not init_path.exists():
        save_weights(init_path, model.parameters())
    root = pm["root"] if cfg["init_from"] else sha256_file(init_path)
    master = tree_map(lambda p: p.astype(mx.float32), model.parameters())
    n = count_params(model)
    fpt = flops_per_token(mcfg, n["total"])

    train = Batches(tokens / "train.bin", ctx, mb, cfg["seed"])
    val = Batches(tokens / "val.bin", ctx, mb, cfg["seed"])
    model.update(tree_map(lambda p: p.astype(dtype), master))
    loss_and_grad = nn.value_and_grad(model, loss_fn)
    if cfg["compile"]:
        # nn.value_and_grad updates the model inside the trace, so its state is an output too;
        # without that the model is left holding tracers after the first call.
        state = [model.state]
        micro = partial(mx.compile, inputs=state, outputs=state)(lambda x, y: loss_and_grad(model, x, y))
    else:
        micro = lambda x, y: loss_and_grad(model, x, y)  # noqa: E731

    if total_steps is None:
        total_steps = calibrate(micro, train, accum, cfg["max_minutes"])

    opt, sched = make_optimizer(cfg, total_steps)
    opt.init(master)
    step, tokens_seen, elapsed_prev, best_val = 0, 0, 0.0, None
    if resume is not None:
        st = load_json(resume / "state.json")
        if st.get("config_digest") != config_digest:
            sys.exit(f"{resume} was written under config {str(st.get('config_digest'))[:16]}, not "
                     f"{str(config_digest)[:16]}; use a fresh --out or restore the original config")
        master = load_weights(resume / "weights.safetensors")
        opt.state = tree_unflatten(list(mx.load(str(resume / "optimizer.safetensors")).items()))
        step, tokens_seen, elapsed_prev, best_val = st["step"], st["tokens_seen"], st["elapsed_s"], st.get("best_val")
        say(f"resumed from {resume.name}: step {step}/{total_steps}")
    model.update(tree_map(lambda p: p.astype(dtype), master))
    mx.eval(model.parameters(), master, opt.state)

    epochs = total_steps * step_tokens / len(train.data)
    say(f"model {mcfg.family}/{mcfg.family_tag} {n['total'] / 1e6:.2f}M params ({n['non_embedding'] / 1e6:.2f}M non-emb), "
        f"ctx {ctx}, {accum}×{mb}×{ctx} = {step_tokens} tokens/step, {total_steps} steps, "
        f"{total_steps * step_tokens / 1e6:.0f}M tokens = {epochs:.2f} epochs of {len(train.data) / 1e6:.0f}M")
    if epochs > 4:
        say(f"warning: {epochs:.1f} epochs; repeated data past ~4 epochs buys little")

    log = JsonlLog(out / "metrics.jsonl")
    log.write(event="start", step=step, total_steps=total_steps, params=n, flops_per_token=fpt,
              step_tokens=step_tokens, model_config=mcfg.to_dict(), config_digest=config_digest, root=root)

    stop = {"sig": None}

    def on_signal(sig, _):
        stop["sig"] = sig
        say(f"signal {sig}: checkpointing after this step")

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    def state_json():
        return {"step": step, "tokens_seen": tokens_seen, "elapsed_s": elapsed_prev + (time.time() - t_start),
                "best_val": best_val, "config_digest": config_digest, "total_steps": total_steps}

    t_start = time.time()
    t_ckpt = t_log = time.time()
    tok_log = 0
    stopped = None
    while step < total_steps:
        loss_sum, grads = None, None
        for m in range(accum):
            x, y = train.get(step, m)
            loss, g = micro(x, y)
            grads = g if grads is None else tree_map(mx.add, grads, g)
            loss_sum = loss if loss_sum is None else loss_sum + loss
            mx.eval(loss_sum, grads)
        grads = tree_map(lambda g: g.astype(mx.float32) / accum, grads)
        grads, gnorm = optim.clip_grad_norm(grads, cfg["grad_clip"])
        master = opt.apply_gradients(grads, master)
        model.update(tree_map(lambda p: p.astype(dtype), master))
        mx.eval(master, opt.state, model.parameters())
        step += 1
        tokens_seen += step_tokens
        tok_log += step_tokens

        if step % cfg["log_every"] == 0 or step == total_steps:
            now = time.time()
            tps = tok_log / (now - t_log)
            loss_v = (loss_sum / accum).item()
            lr = sched(mx.array(step - 1)).item()
            log.write(event="train", step=step, loss=round(loss_v, 5), lr=lr, grad_norm=round(gnorm.item(), 4),
                      tokens_seen=tokens_seen, tok_per_s=round(tps), tflops=round(tps * fpt / 1e12, 3),
                      elapsed_s=round(elapsed_prev + now - t_start, 1))
            say(f"step {step:6d}/{total_steps}  loss {loss_v:.4f}  lr {lr:.2e}  |g| {gnorm.item():.3f}  "
                f"{tps / 1e3:6.1f}k tok/s  {tps * fpt / 1e12:.2f} TFLOPS")
            t_log, tok_log = now, 0

        if step % cfg["eval_every"] == 0 or step == total_steps:
            v = evaluate(model, val, cfg["eval_batches"])
            best_val = v if best_val is None else min(best_val, v)
            log.write(event="eval", step=step, val_loss=round(v, 5), val_ppl=round(math.exp(min(v, 50)), 3))
            say(f"  eval  val_loss {v:.4f}  ppl {math.exp(min(v, 50)):.1f}")

        minutes = (time.time() - t_start) / 60
        if cfg["max_minutes"] and minutes >= cfg["max_minutes"]:
            stopped = "max_minutes"
        if stop["sig"] is not None:
            stopped = f"signal {stop['sig']}"
        if stopped or (time.time() - t_ckpt) / 60 >= cfg["ckpt_minutes"]:
            d = ck.save(step, master, opt, state_json())
            log.write(event="checkpoint", step=step, dir=d.name)
            t_ckpt = time.time()
        if stopped:
            break

    if stopped and stopped.startswith("signal"):
        say(f"stopped ({stopped}) at step {step}; re-run the same command to resume")
        sys.exit(130)

    # Final artifact: fp32 weights and a description of them.
    save_weights(out / "model.safetensors", master)
    final_val = evaluate(model, val, cfg["eval_batches"])
    desc = {
        "schema": "topak.slm.model/0",
        "model_config": mcfg.to_dict(),
        "family_tag": mcfg.family_tag,
        "params": n,
        "root": root,
        "init": init,
        "weights": sha256_file(out / "model.safetensors"),
        "tokenizer": tmeta["tokenizer"],
        "tokens_meta": sha256_file(tokens / "meta.json"),
        "seed": cfg["seed"],
        "config_digest": config_digest,
        "steps": step,
        "total_steps": total_steps,
        "tokens_seen": tokens_seen,
        "stopped": stopped,
        "complete": step >= total_steps,
        "final_val_loss": round(final_val, 5),
        "elapsed_s": round(elapsed_prev + time.time() - t_start, 1),
    }
    write_json(out / "model.json", desc)
    log.write(event="done", **{k: desc[k] for k in ("steps", "tokens_seen", "final_val_loss", "elapsed_s", "weights")})
    if step < total_steps:
        say(f"stopped by the time box at step {step}/{total_steps}; the resume checkpoint is kept, re-run to continue")
    elif not cfg["keep_resume"]:
        shutil.rmtree(ck.dir, ignore_errors=True)
    say(f"done: {step} steps, {tokens_seen / 1e6:.1f}M tokens, val_loss {final_val:.4f}, weights {desc['weights'][:16]}")
    return desc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=pathlib.Path, help="JSON config; its bytes' digest is the trainer config digest")
    ap.add_argument("--tokens", help="directory with train.bin, val.bin, meta.json")
    ap.add_argument("--out", help="checkpoint/output directory")
    ap.add_argument("--preset")
    ap.add_argument("--family", choices=["llama", "ssd"])
    ap.add_argument("--seed", type=int)
    ap.add_argument("--tokens-budget", type=float)
    ap.add_argument("--max-steps", type=int)
    ap.add_argument("--minutes", type=float, help="stop after this much wall-clock time")
    ap.add_argument("--micro-batch", type=int)
    ap.add_argument("--tokens-per-step", type=int)
    ap.add_argument("--dtype", choices=list(DTYPES))
    ap.add_argument("--no-compile", action="store_true")
    a = ap.parse_args()

    if a.config:
        cfg = load_json(a.config)
        path = a.config
    else:
        if not (a.tokens and a.out and a.preset):
            ap.error("without --config, --tokens, --out and --preset are required")
        cfg = {"tokens": a.tokens, "out": a.out, "model": {"family": a.family or "llama", "preset": a.preset}}
        if a.seed is not None:
            cfg["seed"] = a.seed
        if a.tokens_budget:
            cfg["tokens_budget"] = int(a.tokens_budget)
        if a.max_steps:
            cfg["max_steps"] = a.max_steps
        if a.minutes:
            cfg["max_minutes"] = a.minutes
        for k in ("micro_batch", "tokens_per_step", "dtype"):
            if getattr(a, k) is not None:
                cfg[k] = getattr(a, k)
        if a.no_compile:
            cfg["compile"] = False
        path = pathlib.Path(a.out) / "train.config.json"
        write_json(path, cfg)
    run(cfg, config_path=path)


if __name__ == "__main__":
    main()
