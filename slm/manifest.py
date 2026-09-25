#!/usr/bin/env python3
"""The authored manifest for a run, and the *declared* lineage record built from it.

    uv run manifest.py --lineage L-A --corpus data/corpora/fineweb-edu-2024-10 \
        --tokenizer runs/L-A/tokenizer --tokens runs/L-A/tokens --ckpt runs/L-A/ckpt \
        --config runs/L-A/train.config.json --out runs/L-A
    # a fine-tune also passes --parent runs/L-A/lineage.json

`manifest.json` is the SLM session's shape: corpus hash, tokenizer hash, code commit, config and
seed, plus family, root and weights. It is written by whoever ran the training, so under
ADR-0035 it is a claim and never the evidence (§1, Finding 3). For a run made through the
reference mechanism, `lineage/project.py` compares it with the record projected from the log.

`lineage.json` is a record in the ADR §1 schema with strength `declared` at rung 0: a lineage
that can only be declared is D-0035-1. It is what `lineage/independence.py` evaluates for runs
made outside the mechanism.
"""
from __future__ import annotations

import argparse
import getpass
import pathlib
import sys
import time

from common import code_digest, git_commit, load_json, sha256_file, write_json

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lineage"))
import record  # noqa: E402


def build_manifest(lineage: str, corpora: list[pathlib.Path], tokenizer: pathlib.Path, tokens: pathlib.Path,
                   ckpt: pathlib.Path, config: pathlib.Path, parent: dict | None) -> dict:
    model = load_json(ckpt / "model.json")
    tmeta = load_json(tokenizer / "tokenizer.meta.json")
    return {
        "schema": "topak.slm.manifest/0",
        "lineage": lineage,
        "authored": {"by": getpass.getuser(), "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
        "corpus": [{"id": c["id"], "objects_digest": c["objects_digest"],
                    "objects": [{"digest": o["digest"], "bytes": o["bytes"]} for o in c["objects"]],
                    "source": c["source"], "declaration": c["declaration"]}
                   for c in (load_json(d / "corpus.json") for d in corpora)],
        "tokenizer": {"digest": tmeta["digest"], "vocab_size": tmeta["vocab_size"]},
        "tokens": {"meta": sha256_file(tokens / "meta.json"), **load_json(tokens / "meta.json")["splits"]},
        "code": {"git": git_commit(), **code_digest()},
        "config": {"digest": sha256_file(config), "content": load_json(config)},
        "seed": model["seed"],
        "family": model["family_tag"],
        "model": {k: model[k] for k in ("root", "weights", "params", "model_config", "init", "steps", "tokens_seen",
                                        "final_val_loss", "stopped")},
        "parent": {"record": parent["digest"], "lineage": parent["lineage"]} if parent else None,
    }


def declared_record(m: dict, parent: dict | None) -> dict:
    ingress = [record.ingress_entry(o["digest"], o["bytes"], c["declaration"], c["id"])
               for c in m["corpus"] for o in c["objects"]]
    node = {"kind": "finetune" if parent else "pretrain", "corpus": [c["id"] for c in m["corpus"]],
            "trainer": "slm/train.py", "config": m["config"]["digest"], "weights": m["model"]["weights"]}
    return record.build(
        lineage=m["lineage"], strength="declared", rung=0, root=m["model"]["root"], weights=m["model"]["weights"],
        tokenizer=m["tokenizer"]["digest"], family=m["family"],
        trainer={"tool": "slm/train.py", "code": m["code"]["digest"], "config": m["config"]["digest"],
                 "seed": m["seed"]},
        ingress=ingress, parents=[parent] if parent else [], nodes=[node],
        evidence={"source": "authored manifest", "manifest": None})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lineage", required=True)
    ap.add_argument("--corpus", nargs="+", required=True, type=pathlib.Path, help="corpus directories this run read")
    ap.add_argument("--tokenizer", required=True, type=pathlib.Path)
    ap.add_argument("--tokens", required=True, type=pathlib.Path)
    ap.add_argument("--ckpt", required=True, type=pathlib.Path)
    ap.add_argument("--config", required=True, type=pathlib.Path)
    ap.add_argument("--parent", type=pathlib.Path, help="parent lineage.json (fine-tunes)")
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()

    parent = load_json(a.parent) if a.parent else None
    m = build_manifest(a.lineage, a.corpus, a.tokenizer, a.tokens, a.ckpt, a.config, parent)
    write_json(a.out / "manifest.json", m)
    rec = declared_record(m, parent)
    rec["evidence"]["manifest"] = sha256_file(a.out / "manifest.json")
    rec["digest"] = record.sha256_json({k: v for k, v in rec.items() if k != "digest"})
    write_json(a.out / "lineage.json", rec)
    print(f"{a.lineage}: manifest {rec['evidence']['manifest'][:12]}, declared record {rec['digest'][:12]} "
          f"({len(rec['ingress'])} objects, family {rec['family']}, root {rec['root'][:12]})")


if __name__ == "__main__":
    main()
