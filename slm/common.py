"""Shared helpers: digests, canonical JSON, config loading, run logging.

`canonical_json` here is sorted-key, compact JSON. The reference mechanism's
`topak_core::canonical_json` says the same, but in the built binary it is not sorted:
cedar-policy-core turns on serde_json's `preserve_order`, so objects keep insertion order and
structs serialize in field order. They agree on single-key objects and on anything already in
sorted order. lineage/project.py reproduces the reference's field order where it has to (the
params digest). Floats are kept out of anything digested on both sides: serde_json and Python
format some floats differently.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

SLM = pathlib.Path(__file__).resolve().parent
REPO = SLM.parent
DATA = SLM / "data"
RUNS = SLM / "runs"

# The source files whose bytes define "the trainer" for provenance. The code digest covers
# these plus uv.lock. It does not cover the interpreter or the installed wheels (residual:
# shared training stack, ADR-0035 §7).
CODE_FILES = ["common.py", "model.py", "train.py", "train_tokenizer.py", "pretokenize.py", "prepare_corpus.py"]


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_json(value) -> str:
    return sha256_bytes(canonical_json(value))


def sha256_file(path, bufsize: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(bufsize):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(root) -> str:
    """The reference's workspace digest (mechanism.rs `workspace_digest`): SHA-256 over sorted
    (relative path, NUL, bytes, NUL). Equal trees give equal digests on either side."""
    root = pathlib.Path(root)
    h = hashlib.sha256()
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    for rel in files:
        h.update(rel.encode() + b"\0")
        with open(root / rel, "rb") as f:
            while chunk := f.read(1 << 20):
                h.update(chunk)
        h.update(b"\0")
    return h.hexdigest()


def code_digest() -> dict:
    parts = {name: sha256_file(SLM / name) for name in CODE_FILES}
    lock = SLM / "uv.lock"
    parts["uv.lock"] = sha256_file(lock) if lock.exists() else None
    return {"files": parts, "digest": sha256_json(parts)}


def git_commit() -> dict:
    try:
        head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "slm"], capture_output=True,
                               text=True, check=True).stdout.strip() != ""
        return {"commit": head, "slm_dirty": dirty}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"commit": None, "slm_dirty": None}


def load_json(path):
    return json.loads(pathlib.Path(path).read_text())


def write_json(path, value, indent: int = 2):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=indent, sort_keys=False, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


class JsonlLog:
    """Append-only metrics log. One JSON object per line, flushed per write."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "a")

    def write(self, **rec):
        rec.setdefault("t", round(time.time(), 3))
        self.f.write(json.dumps(rec) + "\n")
        self.f.flush()


def corpus_files(objects_dir) -> list[pathlib.Path]:
    """Shards in a fixed order: by file name, which is the content digest (plus `.jsonl` in a
    workspace copy). Hidden and temporary files are skipped."""
    d = pathlib.Path(objects_dir)
    return sorted(p for p in d.iterdir() if p.is_file() and not p.name.startswith("."))


def iter_corpus(objects_dir):
    """(doc id, text) for every document in every shard, in `corpus_files` order."""
    for p in corpus_files(objects_dir):
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    doc = json.loads(line)
                    yield doc.get("id"), doc["text"]


def say(*a):
    """Progress goes to stderr, so a tool speaking MCP on stdout is never corrupted."""
    print(*a, file=sys.stderr, flush=True)
