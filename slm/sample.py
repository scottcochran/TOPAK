#!/usr/bin/env python3
"""Step 8 (evaluate): read samples, and report held-out loss.

    uv run sample.py runs/L-A/ckpt --tokenizer runs/L-A/tokenizer/tokenizer.json \
        --prompt "The history of" -n 3 --tokens runs/L-A/tokens

At 10–50M parameters, benchmarks such as HellaSwag sit near chance and say nothing. Held-out
loss and reading the samples are the evaluation. With `--tokens`, held-out loss is recomputed over
`--eval-batches` fixed windows of `val.bin`, the same windows train.py uses.
"""
from __future__ import annotations

import argparse
import math
import pathlib

import mlx.core as mx

from common import load_json
from model import LM, ModelConfig
from train import Batches, evaluate, load_weights


def load(ckpt: pathlib.Path) -> LM:
    desc = load_json(ckpt / "model.json")
    model = LM(ModelConfig(**desc["model_config"]))
    model.update(load_weights(ckpt / "model.safetensors"))
    mx.eval(model.parameters())
    return model


def generate(model: LM, ids: list[int], n: int, temperature: float, top_k: int, eot: int | None) -> list[int]:
    ctx = model.config.ctx
    out = list(ids)
    for _ in range(n):
        x = mx.array([out[-ctx:]])
        logits = model(x)[0, -1].astype(mx.float32)
        if temperature <= 0:
            nxt = int(mx.argmax(logits).item())
        else:
            logits = logits / temperature
            if top_k:
                kth = mx.sort(logits)[-top_k]
                logits = mx.where(logits < kth, -mx.inf, logits)
            nxt = int(mx.random.categorical(logits).item())
        out.append(nxt)
        if eot is not None and nxt == eot:
            break
    return out[len(ids):]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ckpt", type=pathlib.Path, help="directory with model.json and model.safetensors")
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("-n", "--samples", type=int, default=3)
    ap.add_argument("--max-new", type=int, default=200)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tokens", type=pathlib.Path, help="token directory, to report held-out loss")
    ap.add_argument("--eval-batches", type=int, default=20)
    ap.add_argument("--micro-batch", type=int, default=16)
    a = ap.parse_args()

    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(a.tokenizer)
    eot = tok.token_to_id("<|endoftext|>")
    model = load(a.ckpt)
    mx.random.seed(a.seed)

    if a.tokens:
        desc = load_json(a.ckpt / "model.json")
        val = Batches(a.tokens / "val.bin", model.config.ctx, a.micro_batch, desc["seed"])
        v = evaluate(model, val, a.eval_batches)
        print(f"held-out loss {v:.4f}  perplexity {math.exp(v):.1f}  ({a.eval_batches}×{a.micro_batch} windows)")

    prompt = tok.encode(a.prompt).ids if a.prompt else [eot]
    for i in range(a.samples):
        ids = generate(model, prompt, a.max_new, a.temperature, a.top_k, eot)
        print(f"--- sample {i + 1}")
        print(a.prompt + tok.decode(ids))


if __name__ == "__main__":
    main()
