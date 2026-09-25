#!/usr/bin/env python3
"""Measure E3 overlap for every pair of lineage records, for the independence table.

    uv run lineage/measure_pairs.py runs/small/*/lineage.json --granularity window:256 \
        --out runs/small/overlap

Each record's side is its whole ingress set, as the evaluator requires. Per-object results are
cached (see overlap.py), so each shard is hashed once however many pairs it appears in. Writes one
`topak.overlap/0` report per pair, named `<A>__<B>.json`.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import overlap  # noqa: E402
from common import write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("records", nargs="+", help="lineage.json files (globs allowed)")
    ap.add_argument("--granularity", default="window:256")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    paths = sorted({p for pat in a.records for p in (glob.glob(pat) or [pat])})
    recs = {json.loads(Path(p).read_text())["lineage"]: p for p in paths}
    params = {"granularity": a.granularity, "ngram": 5, "perms": 112, "bands": 14, "rows": 8, "seed": 35,
              "normalization": overlap.NORMALIZATION}
    t0 = time.time()
    sides = {}
    for name, p in recs.items():
        files = overlap.resolve_side([p])
        sides[name] = {"files": files, "m": overlap.measure_side(files, params, a.workers)}
        print(f"{name:<12} {len(files):4d} objects  {len(sides[name]['m']['exact']):>9,} units  "
              f"{time.time() - t0:6.0f}s", file=sys.stderr)
    print(f"{'pair':<28} {'exact':>9} {'near':>9}  (share of the smaller set, {a.granularity})")
    for x, y in combinations(sorted(recs), 2):
        rep = overlap.build_report({"a": sides[x], "b": sides[y]}, params, {"a": [recs[x]], "b": [recs[y]]},
                                   False, t0)
        write_json(a.out / f"{x}__{y}.json", rep)
        print(f"{x + ' / ' + y:<28} {rep['exact']['share_of_smaller']:9.5f} {rep['near']['share_of_smaller']:9.5f}")


if __name__ == "__main__":
    main()
