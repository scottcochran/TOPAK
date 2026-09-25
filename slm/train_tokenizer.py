#!/usr/bin/env python3
"""Step 3a: train a byte-level BPE tokenizer on a corpus slice.

    uv run train_tokenizer.py --objects data/corpora/fineweb-edu-2024-10/objects \
        --out runs/L-A/tokenizer --vocab 16384

A 16k vocabulary keeps the embedding table from eating a small model: at d_model 512 it is 8.4M
parameters, against 16.8M at 32k. Byte-level BPE needs no <unk> and round-trips any UTF-8.

Training reads a deterministic, evenly strided sample of documents (every k-th, with k chosen
so the sample is about `sample_bytes`) rather than the head of the corpus, so the merges are not
fitted to the first shard's sites or books.
"""
from __future__ import annotations

import argparse
import math
import pathlib

from common import corpus_files, iter_corpus, say, sha256_file, write_json

EOT = "<|endoftext|>"


def train(cfg: dict, base: pathlib.Path = pathlib.Path(".")) -> dict:
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

    objects = base / cfg["objects"]
    out = base / cfg["out"]
    vocab = int(cfg.get("vocab_size", 16384))
    sample_bytes = int(cfg.get("sample_bytes", 500_000_000))
    assert vocab <= 65535, "pretokenize stores ids as uint16"

    total = sum(p.stat().st_size for p in corpus_files(objects))
    stride = max(1, math.ceil(total / sample_bytes))
    seen = {"docs": 0, "bytes": 0}

    def sample():
        for i, (_, text) in enumerate(iter_corpus(objects)):
            if i % stride == 0:
                seen["docs"] += 1
                seen["bytes"] += len(text.encode())
                yield text

    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab,
        min_frequency=int(cfg.get("min_frequency", 2)),
        special_tokens=[EOT],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    say(f"tokenizer: {vocab} merges target, stride {stride} over {total / 1e6:.0f} MB")
    tok.train_from_iterator(sample(), trainer=trainer)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "tokenizer.json"
    tok.save(str(path))
    meta = {
        "schema": "topak.slm.tokenizer/0",
        "vocab_size": tok.get_vocab_size(),
        "eot_id": tok.token_to_id(EOT),
        "digest": sha256_file(path),
        "sample": {"stride": stride, **seen},
        "config": cfg,
    }
    write_json(out / "tokenizer.meta.json", meta)
    say(f"tokenizer: {meta['vocab_size']} tokens from {seen['docs']} docs, digest {meta['digest'][:16]}")
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--objects", required=True, help="directory of corpus shards")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--vocab", type=int, default=16384)
    ap.add_argument("--sample-bytes", type=float, default=5e8)
    a = ap.parse_args()
    train({"objects": a.objects, "out": a.out, "vocab_size": a.vocab, "sample_bytes": int(a.sample_bytes)})


if __name__ == "__main__":
    main()
