#!/usr/bin/env python3
"""Step 2 (data): cut a reproducible slice of a catalogued corpus into content-addressed shards.

    uv run prepare_corpus.py fineweb-edu-2024-10 --max-bytes 4e9
    uv run prepare_corpus.py pg19 --max-bytes 8e6 --shard-bytes 1e6 --out data/corpora/pg19-rehearsal

Long documents (whole books) are cut at paragraph breaks into pieces of at most the catalogue's
`max_doc_chars`, each a document with id `<source id>#<k>`. That gives the held-out split and the
E3 overlap tool units of a useful size.

The source is read in a fixed order (files as listed in corpora.json, row groups in file order,
rows in row-group order) from a pinned dataset revision, streamed over HTTP, so only the bytes
needed are downloaded. Each shard is JSONL, one `{"id", "text"}` document per line, and is named
by the SHA-256 of its bytes. That is exactly the reference mechanism's corpus layout, so the
shards can be mounted as its corpus root unchanged.

The output directory holds `objects/<sha256>` and `corpus.json`: the source pins, the slice
parameters, every object's digest and size, and the admission declaration copied from the
catalogue. The same arguments always produce the same objects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

from common import DATA, SLM, load_json, say, sha256_file, sha256_json, write_json

EST_BYTES_PER_TOKEN = 4.0  # English, 16k byte-level BPE. Replaced by the measured value after pretokenize.


def iter_docs(source: dict, skip_docs: int):
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    fs = HfFileSystem()
    text_col, id_col = source["text_column"], source.get("id_column")
    cols = [text_col] + ([id_col] if id_col else [])
    n = 0
    for rel in source["files"]:
        path = f"datasets/{source['hf_repo']}@{source['revision']}/{rel}"
        with fs.open(path, "rb", block_size=16 << 20) as f:
            pf = pq.ParquetFile(f)
            for batch in pf.iter_batches(batch_size=1000, columns=cols):
                texts = batch.column(text_col).to_pylist()
                ids = batch.column(id_col).to_pylist() if id_col else [None] * len(texts)
                for i, t in zip(ids, texts):
                    n += 1
                    if n <= skip_docs or not t:
                        continue
                    yield (i if i is not None else f"{rel}#{n - 1}"), t


def split_doc(text: str, max_chars: int):
    """Cut a long document (a whole book) into pieces of at most `max_chars`, at a paragraph
    break where one falls in the second half of the window, else at a line break, else hard."""
    if not max_chars or len(text) <= max_chars:
        yield text
        return
    while len(text) > max_chars:
        cut = text.rfind("\n\n", 0, max_chars)
        if cut < max_chars // 2:
            cut = text.rfind("\n", 0, max_chars)
        if cut < max_chars // 2:
            cut = max_chars
        yield text[:cut]
        text = text[cut:].lstrip("\n")
    if text:
        yield text


class ShardWriter:
    def __init__(self, objects: pathlib.Path, shard_bytes: int):
        self.objects, self.limit = objects, shard_bytes
        self.objects.mkdir(parents=True, exist_ok=True)
        self.tmp = self.objects / ".shard.tmp"
        self.f, self.h, self.size, self.docs = None, None, 0, 0
        self.done: list[dict] = []

    def add(self, line: bytes):
        if self.f is None:
            self.f, self.h, self.size, self.docs = open(self.tmp, "wb"), hashlib.sha256(), 0, 0
        self.f.write(line)
        self.h.update(line)
        self.size += len(line)
        self.docs += 1
        if self.size >= self.limit:
            self.close()

    def close(self):
        if self.f is None:
            return
        self.f.close()
        d = self.h.hexdigest()
        os.replace(self.tmp, self.objects / d)
        self.done.append({"digest": d, "bytes": self.size, "docs": self.docs})
        say(f"  shard {len(self.done):4d}  {d[:16]}  {self.size / 1e6:7.1f} MB  {self.docs} docs")
        self.f = None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpus", help="an id from corpora.json")
    ap.add_argument("--max-bytes", type=float, required=True, help="stop after this many shard bytes (4e9 ≈ 1B tokens)")
    ap.add_argument("--shard-bytes", type=float, default=64e6)
    ap.add_argument("--skip-docs", type=int, default=0, help="skip the first N documents of the source order")
    ap.add_argument("--min-chars", type=int, default=64, help="drop documents shorter than this")
    ap.add_argument("--out", type=pathlib.Path, help="default: data/corpora/<corpus>")
    ap.add_argument("--catalogue", type=pathlib.Path, default=SLM / "corpora.json")
    a = ap.parse_args()

    entry = load_json(a.catalogue)["corpora"].get(a.corpus)
    if entry is None:
        sys.exit(f"unknown corpus {a.corpus!r}; see {a.catalogue}")
    out = a.out or DATA / "corpora" / a.corpus
    max_doc_chars = entry["source"].get("max_doc_chars", 0)
    slice_ = {"max_bytes": int(a.max_bytes), "shard_bytes": int(a.shard_bytes), "skip_docs": a.skip_docs,
              "min_chars": a.min_chars, "max_doc_chars": max_doc_chars}
    manifest_path = out / "corpus.json"
    if manifest_path.exists():
        old = load_json(manifest_path)
        if old.get("source") == entry["source"] and old.get("slice") == slice_:
            say(f"{out}: already prepared with these parameters ({len(old['objects'])} objects)")
            return
        sys.exit(f"{out} holds a different slice; remove it or pass --out")

    say(f"{a.corpus}: {entry['source']['hf_repo']}@{entry['source']['revision'][:12]}, up to {a.max_bytes / 1e6:.0f} MB")
    w = ShardWriter(out / "objects", int(a.shard_bytes))
    total = 0
    for doc_id, text in iter_docs(entry["source"], a.skip_docs):
        if len(text) < a.min_chars:
            continue
        pieces = list(split_doc(text, max_doc_chars))
        for k, piece in enumerate(pieces):
            pid = doc_id if len(pieces) == 1 else f"{doc_id}#{k}"
            line = (json.dumps({"id": pid, "text": piece}, ensure_ascii=False) + "\n").encode()
            w.add(line)
            total += len(line)
            if total >= a.max_bytes:
                break
        if total >= a.max_bytes:
            break
    w.close()

    manifest = {
        "schema": "topak.slm.corpus/0",
        "id": a.corpus,
        "source": entry["source"],
        "slice": slice_,
        "declaration": entry["declaration"],
        "objects": w.done,
        "bytes": total,
        "docs": sum(o["docs"] for o in w.done),
        "est_tokens": int(total / EST_BYTES_PER_TOKEN),
        "prepared_by": {"tool": "prepare_corpus.py", "digest": sha256_file(__file__)},
    }
    manifest["objects_digest"] = sha256_json(sorted(o["digest"] for o in w.done))
    write_json(manifest_path, manifest)
    say(f"{out}: {len(w.done)} objects, {total / 1e6:.1f} MB, {manifest['docs']} docs, ~{manifest['est_tokens'] / 1e6:.0f}M tokens")


if __name__ == "__main__":
    main()
