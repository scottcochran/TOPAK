#!/usr/bin/env python3
"""Mechanical citation checks for an audit.

    check_citations.py <file> [--root DIR]

Reports each backticked path that does not exist, and each `path` (`<hex>`) or path (sha256 <hex>) citation whose digest
does not match the file. A mismatch may be a file that legitimately moved: check its history before calling it wrong.
Exits 1 if anything did not match. It reads form only.
"""
import argparse
import hashlib
import pathlib
import re
import sys

DIGEST = re.compile(r"`([\w./-]+\.[A-Za-z0-9]+)`\s*\(`?(?:sha256 )?([0-9a-f]{12,64})…?`?\)")
AT = re.compile(r"`([\w./-]+\.[A-Za-z0-9]+)`\s+(?:is\s+)?at\s+(?:digest\s+)?`([0-9a-f]{12,64})`")
PLAIN = re.compile(r"(?<![\w/.-])([\w./-]+\.[A-Za-z0-9]+) \(sha256 ([0-9a-f]{12,64})\)")
PATH = re.compile(r"`((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]+)`")


def find_root(start):
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--root", type=pathlib.Path)
    a = ap.parse_args()
    root = (a.root or find_root(a.file.resolve().parent)).resolve()
    text = a.file.read_text()
    seen, ok, bad, missing = set(), 0, [], []
    for rel, digest in DIGEST.findall(text) + AT.findall(text) + PLAIN.findall(text):
        if (rel, digest) in seen:
            continue
        seen.add((rel, digest))
        p = root / rel
        if not p.is_file():
            missing.append(f"{rel} (cited at {digest})")
        elif hashlib.sha256(p.read_bytes()).hexdigest().startswith(digest):
            ok += 1
        else:
            bad.append(f"{rel}: cited {digest}, file is {hashlib.sha256(p.read_bytes()).hexdigest()[:len(digest)]}")
    paths = sorted(set(PATH.findall(text)))
    absent = [p for p in paths if not (root / p).exists() and not any(p in m for m in missing)]
    print(f"digests: {ok} match, {len(bad)} differ, {len(missing)} of missing files; paths: {len(paths) - len(absent)} of {len(paths)} exist")
    for b in bad:
        print(f"DIFFERS {b}")
    for m in missing:
        print(f"MISSING {m}")
    for p in absent:
        print(f"NO SUCH PATH {p}")
    return 1 if bad or missing or absent else 0


if __name__ == "__main__":
    sys.exit(main())
