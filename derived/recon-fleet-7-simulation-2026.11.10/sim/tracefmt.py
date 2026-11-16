"""The trace format, shared by the simulator and the replay tool.

A trace is gzip of one JSON object per line. Line 0 is the header. Every later line is an event, whose
`patch` is the only thing that changes state, so applying the patches in order rebuilds the state with
no simulator, no policy engine and no random numbers.

    patch op:  ["s", "a/b/c", value]   set
               ["d", "a/b/c"]          delete
"""
import gzip
import hashlib
import json


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def state_hash(state):
    return sha(canonical(state))


def event_hash(ev):
    return sha(canonical({k: v for k, v in ev.items() if k != "hash"}))


def apply_patch(state, patch):
    for op in patch:
        keys = op[1].split("/")
        node = state
        for k in keys[:-1]:
            node = node[k]
        if op[0] == "s":
            node[keys[-1]] = json.loads(json.dumps(op[2]))
        else:
            del node[keys[-1]]


def write_trace(path, lines):
    with open(path, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for line in lines:
                gz.write(line.encode() + b"\n")


def read_trace(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    return lines[0], lines[1:]
