#!/usr/bin/env python3
"""Run one or more lineages from lineages.json end to end, idempotently.

    uv run pipeline.py L-A --profile small
    uv run pipeline.py L-A L-B L-C L-D L-T L-T2 L-E5 L-A-prime --profile small
    ./run_long.sh L-A --profile full        # the same, under caffeinate, on AC power

Steps per lineage, each skipped when its output already exists:

  prepare     data/corpora/<corpus>@<profile>/     content-addressed shards + corpus.json
  tokenizer   runs/<profile>/<L>/tokenizer/        16k byte-level BPE (or `tokenizer_from`)
  pretokenize runs/<profile>/<L>/tokens/           train.bin, val.bin, meta.json
  train       runs/<profile>/<L>/ckpt/             resumable; init.safetensors, model.safetensors
  manifest    runs/<profile>/<L>/                  manifest.json (authored), lineage.json (declared)

`init_from` and `tokenizer_from` lineages must be run first. The train config is written with
sorted keys, so re-running produces the same bytes and the resume check passes.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

from common import DATA, RUNS, SLM, load_json, say

STEPS = ["prepare", "tokenizer", "pretokenize", "train", "manifest"]


def sh(*args):
    say("$ " + " ".join(str(a) for a in args))
    rc = subprocess.run([sys.executable, *map(str, args)], cwd=SLM).returncode
    if rc:
        sys.exit(rc)  # 130 from an interrupted trainer reaches run_long.sh as "stopped by operator"


def run_lineage(name: str, profile: str, steps: list[str], cat: dict):
    L = cat["lineages"][name]
    P = cat["profiles"][profile]
    scale = L.get("corpus_scale", 1)
    corpus_dir = DATA / "corpora" / (f"{L['corpus']}@{profile}" + (f"x{scale}" if scale != 1 else ""))
    run = RUNS / profile / name
    tok_dir = RUNS / profile / L["tokenizer_from"] / "tokenizer" if L.get("tokenizer_from") else run / "tokenizer"
    tokens, ckpt = run / "tokens", run / "ckpt"
    run.mkdir(parents=True, exist_ok=True)
    say(f"== {name} ({profile}): {L['corpus']}, {L['family']}, preset {P['preset']}")

    if "prepare" in steps and not (corpus_dir / "corpus.json").exists():
        sh("prepare_corpus.py", L["corpus"], "--max-bytes", P["corpus_max_bytes"] * scale, "--out", corpus_dir)
    if "tokenizer" in steps and not L.get("tokenizer_from") and not (tok_dir / "tokenizer.meta.json").exists():
        sh("train_tokenizer.py", "--objects", corpus_dir / "objects", "--out", tok_dir)
    if "pretokenize" in steps and not (tokens / "meta.json").exists():
        sh("pretokenize.py", "--objects", corpus_dir / "objects", "--tokenizer", tok_dir / "tokenizer.json",
           "--out", tokens)
    config = run / "train.config.json"
    done = (ckpt / "model.json").exists() and load_json(ckpt / "model.json").get("complete", True)
    if "train" in steps and not done:
        cfg = {
            "tokens": str(tokens.relative_to(SLM)), "out": str(ckpt.relative_to(SLM)), "seed": L["seed"],
            "model": {"family": L["family"], "preset": P["preset"]},
            "tokens_budget": int(P["tokens_budget"] * L.get("budget_frac", 1.0)),
            "micro_batch": P["micro_batch"],
            "tokens_per_step": P["tokens_per_step"],
        }
        for k in ("lr_peak", "warmup_frac"):
            if k in L:
                cfg[k] = L[k]
        if L.get("init_from"):
            cfg["init_from"] = str((RUNS / profile / L["init_from"] / "ckpt").relative_to(SLM))
        config.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
        sh("train.py", "--config", config)
    if "manifest" in steps:
        args = ["manifest.py", "--lineage", name, "--corpus", corpus_dir, "--tokenizer", tok_dir, "--tokens", tokens,
                "--ckpt", ckpt, "--config", config, "--out", run]
        if L.get("init_from"):
            args += ["--parent", RUNS / profile / L["init_from"] / "lineage.json"]
        sh(*args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lineages", nargs="+")
    ap.add_argument("--profile", default="small")
    ap.add_argument("--steps", default=",".join(STEPS), help=f"comma list from {STEPS}")
    a = ap.parse_args()
    cat = load_json(SLM / "lineages.json")
    steps = a.steps.split(",")
    for s in steps:
        if s not in STEPS:
            ap.error(f"unknown step {s}")
    for name in a.lineages:
        if name not in cat["lineages"]:
            ap.error(f"unknown lineage {name}; see lineages.json")
        run_lineage(name, a.profile, steps, cat)


if __name__ == "__main__":
    main()
