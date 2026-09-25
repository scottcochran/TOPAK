#!/usr/bin/env python3
"""Step 3b: tokenize a corpus once into flat uint16 token files, nanoGPT-style.

    uv run pretokenize.py --objects data/corpora/fineweb-edu-2024-10/objects \
        --tokenizer runs/L-A/tokenizer/tokenizer.json --out runs/L-A/tokens

Writes `train.bin` and `val.bin` (little-endian uint16, one <|endoftext|> after every document)
and `meta.json`. Training memory-maps the files, so the corpus never has to fit in RAM.

The held-out split is by document content: a document is in `val` if the first two bytes of the
SHA-256 of its text, mod 1000, fall below `val_permille`. The split does not depend on shard
order, and an identical document never lands on both sides.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib

import numpy as np

from common import corpus_files, iter_corpus, say, sha256_file, write_json

BATCH_DOCS = 2048


def run(cfg: dict, base: pathlib.Path = pathlib.Path(".")) -> dict:
    from tokenizers import Tokenizer

    objects = base / cfg["objects"]
    tok_path = base / cfg["tokenizer"]
    out = base / cfg["out"]
    permille = int(cfg.get("val_permille", 5))
    tok = Tokenizer.from_file(str(tok_path))
    eot = tok.token_to_id("<|endoftext|>")
    assert tok.get_vocab_size() <= 65535 and eot is not None

    out.mkdir(parents=True, exist_ok=True)
    files = {s: open(out / f"{s}.bin", "wb") for s in ("train", "val")}
    counts = {s: {"docs": 0, "tokens": 0, "bytes": 0} for s in files}
    batch: list[tuple[str, str]] = []

    def flush():
        encs = tok.encode_batch([t for _, t in batch])
        for (split, text), e in zip(batch, encs):
            ids = np.asarray(e.ids + [eot], dtype=np.uint16)
            ids.tofile(files[split])
            c = counts[split]
            c["docs"] += 1
            c["tokens"] += len(ids)
            c["bytes"] += len(text.encode())
        batch.clear()

    for _, text in iter_corpus(objects):
        h = hashlib.sha256(text.encode()).digest()
        split = "val" if int.from_bytes(h[:2], "big") % 1000 < permille else "train"
        batch.append((split, text))
        if len(batch) >= BATCH_DOCS:
            flush()
            if counts["train"]["docs"] % (BATCH_DOCS * 50) == 0:
                say(f"  {counts['train']['tokens'] / 1e6:8.1f}M train tokens")
    if batch:
        flush()
    for f in files.values():
        f.close()

    meta = {
        "schema": "topak.slm.tokens/0",
        "dtype": "uint16",
        "eot_id": eot,
        "vocab_size": tok.get_vocab_size(),
        "tokenizer": sha256_file(tok_path),
        "objects": [p.name for p in corpus_files(objects)],
        "val_permille": permille,
        "splits": counts,
        "bytes_per_token": round(counts["train"]["bytes"] / max(1, counts["train"]["tokens"]), 4),
        "bins": {s: sha256_file(out / f"{s}.bin") for s in files},
        "config": cfg,
    }
    write_json(out / "meta.json", meta)
    say(f"tokens: train {counts['train']['tokens'] / 1e6:.1f}M, val {counts['val']['tokens'] / 1e6:.2f}M, "
        f"{meta['bytes_per_token']} bytes/token")
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--objects", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--val-permille", type=int, default=5)
    a = ap.parse_args()
    run({"objects": a.objects, "tokenizer": a.tokenizer, "out": a.out, "val_permille": a.val_permille})


if __name__ == "__main__":
    main()
