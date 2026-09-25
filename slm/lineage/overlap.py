#!/usr/bin/env python3
"""ADR-0035 §8: measure E3's corpus overlap between two ingress sets, without training.

    uv run lineage/overlap.py --a data/corpora/fineweb-edu-2024-10 --b data/corpora/fineweb-2024-10 \
        --out runs/overlap/edu-vs-fineweb.json
    uv run lineage/overlap.py --a runs/L-A/lineage.json --b runs/L-B/lineage.json --granularity window:256

Each side is one or more corpus directories (corpus.json + objects/) or lineage records, whose
ingress objects are found under data/corpora/*/objects. The report's `ingress_set` is the digest
of the sorted object digests measured, the key the independence evaluator matches a pair of
records against. A measurement of fewer objects than a record's ingress does not cover it, and
E3 then fails closed.

Units and normalization. A unit is a document (`doc`) or a run of N words (`window:N`, for
books, where a whole document is far too coarse). Text is NFKC-normalized, lower-cased, reduced
to letters and digits and whitespace-collapsed before hashing.

- exact: SHA-256 of the normalized unit. A unit matches if the other side has the same hash.
- near: MinHash over word 5-grams, 112 permutations in 14 bands of 8 rows (FineWeb's own dedup
  parameters). A unit matches if any band collides with a unit on the other side. The banding
  S-curve puts the 50% detection point near Jaccard 0.72. Pairs are not re-verified, so a few
  matches may sit below that. Near matches include exact ones.

For each side the report gives matched units and matched bytes, and `share_of_smaller`: matched
bytes on the smaller side (by normalized bytes) over that side's bytes, which is the ADR's E3
quantity. `tool` is the SHA-256 of this file. With `params`, it is what a threshold file pins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import DATA, RUNS, sha256_file, sha256_json, write_json  # noqa: E402

NORMALIZATION = "nfkc-lower-alnum-v1"
P31 = (1 << 31) - 1
_NONWORD = re.compile(r"[\W_]+", re.UNICODE)


def normalize(text: str) -> str:
    return _NONWORD.sub(" ", unicodedata.normalize("NFKC", text).lower()).strip()


class MinHasher:
    def __init__(self, ngram: int, perms: int, bands: int, seed: int):
        assert perms % bands == 0
        self.k, self.perms, self.bands, self.rows = ngram, perms, bands, perms // bands
        rng = np.random.default_rng(seed)
        self.a = rng.integers(1, P31, perms, dtype=np.uint64)
        self.b = rng.integers(0, P31, perms, dtype=np.uint64)
        self.powers = np.array([pow(1_000_003, ngram - 1 - i, 1 << 64) for i in range(ngram)], dtype=np.uint64)
        self.mix = rng.integers(1, 1 << 63, self.rows, dtype=np.uint64) | np.uint64(1)
        self.cache: dict[str, int] = {}

    def word_ids(self, words: list[str]) -> np.ndarray:
        c = self.cache
        if len(c) > 2_000_000:
            c.clear()
        out = np.empty(len(words), dtype=np.uint64)
        for i, w in enumerate(words):
            v = c.get(w)
            if v is None:
                v = c[w] = int.from_bytes(hashlib.blake2b(w.encode(), digest_size=8).digest(), "little")
            out[i] = v
        return out

    def band_keys(self, words: list[str]) -> np.ndarray | None:
        """(bands,) uint64 keys, or None for a unit shorter than one shingle."""
        n = len(words) - self.k + 1
        if n < 1:
            return None
        w = self.word_ids(words)
        with np.errstate(over="ignore"):
            sh = np.zeros(n, dtype=np.uint64)
            for i in range(self.k):
                sh += w[i:i + n] * self.powers[i]
            x = (sh ^ (sh >> np.uint64(31))) & np.uint64(P31)
            sig = np.full(self.perms, np.iinfo(np.uint64).max, dtype=np.uint64)
            for s in range(0, n, 20000):
                xs = x[s:s + 20000]
                sig = np.minimum(sig, ((self.a[:, None] * xs[None, :] + self.b[:, None]) % np.uint64(P31)).min(axis=1))
            rows = sig.reshape(self.bands, self.rows)
            keys = (rows * self.mix[None, :]).sum(axis=1)
            keys ^= np.arange(self.bands, dtype=np.uint64) * np.uint64(0x9E3779B97F4A7C15)
        return keys


def units(text: str, granularity: str):
    norm = normalize(text)
    if granularity == "doc":
        if norm:
            yield norm
        return
    n = int(granularity.split(":", 1)[1])
    words = norm.split()
    for s in range(0, len(words), n):
        chunk = words[s:s + n]
        if chunk:
            yield " ".join(chunk)


def process_object(args) -> dict:
    path, granularity, ngram, perms, bands, seed, cache = args
    if cache:
        cpath = Path(cache) / f"{Path(path).name}.npz"
        if cpath.exists():
            z = np.load(cpath)
            return {k: z[k] for k in ("exact", "bytes", "keys", "has")}
    mh = MinHasher(ngram, perms, bands, seed)
    ex, nb, keys, has = [], [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            for u in units(json.loads(line)["text"], granularity):
                b = u.encode()
                ex.append(int.from_bytes(hashlib.sha256(b).digest()[:8], "little"))
                nb.append(len(b))
                k = mh.band_keys(u.split())
                has.append(k is not None)
                keys.append(k if k is not None else np.zeros(bands, dtype=np.uint64))
    out = {"exact": np.array(ex, dtype=np.uint64), "bytes": np.array(nb, dtype=np.int64),
           "keys": np.stack(keys) if keys else np.zeros((0, bands), dtype=np.uint64),
           "has": np.array(has, dtype=bool)}
    if cache:
        Path(cache).mkdir(parents=True, exist_ok=True)
        tmp = Path(cache) / f".{Path(path).name}.{os.getpid()}.npz"
        np.savez(tmp, **out)
        os.replace(tmp, cpath)
    return out


def resolve_side(inputs: list[str]) -> list[Path]:
    """Object files for one side: from corpus directories, or lineage records' ingress."""
    index = None
    files: dict[str, Path] = {}
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            for f in sorted((p / "objects").iterdir()):
                if not f.name.startswith("."):
                    files[f.name] = f
        else:
            rec = json.loads(p.read_text())
            if index is None:
                index = {f.name: f for f in DATA.glob("corpora/*/objects/*")}
            for e in rec["ingress"]:
                if e["digest"] not in index:
                    sys.exit(f"{p}: ingress object {e['digest'][:16]} not found under {DATA}/corpora/*/objects")
                files[e["digest"]] = index[e["digest"]]
    return [files[d] for d in sorted(files)]


def cache_dir(params: dict) -> Path:
    """Per-object results depend only on the object's bytes, the parameters and this file, so they
    are cached under a digest of all three's non-object parts."""
    return RUNS / "overlap-cache" / sha256_json({**params, "tool": sha256_file(__file__)})[:16]


def measure_side(files, params, workers, cache=True) -> dict:
    c = str(cache_dir(params)) if cache else None
    jobs = [(str(f), params["granularity"], params["ngram"], params["perms"], params["bands"], params["seed"], c)
            for f in files]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(process_object, jobs))
    cat = lambda k: np.concatenate([p[k] for p in parts]) if parts else np.zeros(0)  # noqa: E731
    return {"exact": cat("exact"), "bytes": cat("bytes"), "keys": np.concatenate([p["keys"] for p in parts]),
            "has": cat("has")}


def matched(x: dict, y: dict) -> dict:
    ex = np.isin(x["exact"], y["exact"])
    ykeys = y["keys"][y["has"]].ravel()
    nr = np.zeros(len(x["exact"]), dtype=bool)
    if len(ykeys) and x["has"].any():
        hit = np.isin(x["keys"], ykeys).any(axis=1) & x["has"]
        nr = hit
    nr |= ex
    return {"exact_units": int(ex.sum()), "exact_bytes": int(x["bytes"][ex].sum()),
            "near_units": int(nr.sum()), "near_bytes": int(x["bytes"][nr].sum())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", nargs="+", required=True, help="corpus dirs or lineage.json files")
    ap.add_argument("--b", nargs="+", required=True)
    ap.add_argument("--granularity", default="doc", help="doc | window:<words>")
    ap.add_argument("--ngram", type=int, default=5)
    ap.add_argument("--perms", type=int, default=112)
    ap.add_argument("--bands", type=int, default=14)
    ap.add_argument("--seed", type=int, default=35)
    ap.add_argument("--max-objects", type=int, help="measure only the first N objects per side (exploration; "
                                                     "the result then covers no full lineage)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.granularity != "doc" and not re.fullmatch(r"window:\d+", a.granularity):
        ap.error("--granularity is doc or window:<words>")

    params = {"granularity": a.granularity, "ngram": a.ngram, "perms": a.perms, "bands": a.bands,
              "rows": a.perms // a.bands, "seed": a.seed, "normalization": NORMALIZATION}
    t0 = time.time()
    sides = {}
    for name, inputs in (("a", a.a), ("b", a.b)):
        files = resolve_side(inputs)[: a.max_objects]
        print(f"{name}: {len(files)} objects from {', '.join(inputs)}", file=sys.stderr)
        m = measure_side(files, params, a.workers)
        sides[name] = {"files": files, "m": m}
        print(f"   {len(m['exact']):,} units, {int(m['bytes'].sum()) / 1e6:,.1f} MB normalized, "
              f"{time.time() - t0:.0f}s", file=sys.stderr)

    report = build_report(sides, params, {"a": a.a, "b": a.b}, a.max_objects is not None, t0)
    ra, rb = report["a"], report["b"]
    for name, s in (("a", ra), ("b", rb)):
        print(f"{name}: exact {s['exact_units']:,} units / {s['exact_bytes'] / 1e6:,.2f} MB · "
              f"near {s['near_units']:,} units / {s['near_bytes'] / 1e6:,.2f} MB  of {s['units']:,} units, "
              f"{s['bytes'] / 1e6:,.1f} MB")
    print(f"share of the smaller set ({report['smaller']}): exact {report['exact']['share_of_smaller']:.5f} · "
          f"near {report['near']['share_of_smaller']:.5f}   [{a.granularity}, tool {report['tool'][:12]}]")
    if a.out:
        write_json(a.out, report)


def build_report(sides: dict, params: dict, inputs: dict, partial: bool, t0: float) -> dict:
    ma, mb = sides["a"]["m"], sides["b"]["m"]
    ra, rb = matched(ma, mb), matched(mb, ma)
    ba, bb = int(ma["bytes"].sum()), int(mb["bytes"].sum())
    small = "a" if ba <= bb else "b"
    rs, denom = (ra, ba) if small == "a" else (rb, bb)

    def side(name, s, r):
        return {"inputs": inputs[name], "ingress_set": sha256_json(sorted(f.name for f in s["files"])),
                "objects": len(s["files"]), "units": int(len(s["m"]["exact"])),
                "units_hashed": int(s["m"]["has"].sum()), "bytes": int(s["m"]["bytes"].sum()), **r}

    report = {
        "schema": "topak.overlap/0",
        "tool": sha256_file(__file__),
        "params": params,
        "a": side("a", sides["a"], ra),
        "b": side("b", sides["b"], rb),
        "smaller": small,
        "exact": {"share_of_smaller": rs["exact_bytes"] / max(1, denom),
                  "matched_bytes_a": ra["exact_bytes"], "matched_bytes_b": rb["exact_bytes"]},
        "near": {"share_of_smaller": rs["near_bytes"] / max(1, denom),
                 "matched_bytes_a": ra["near_bytes"], "matched_bytes_b": rb["near_bytes"]},
        "partial": partial,
        "elapsed_s": round(time.time() - t0, 1),
    }
    return report


if __name__ == "__main__":
    main()
