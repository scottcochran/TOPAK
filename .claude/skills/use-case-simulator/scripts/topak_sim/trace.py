"""The trace format, shared by the simulator and the replay tool.

A trace is gzip of one JSON object per line. Line 0 is the header. Every later line is an event, whose
`patch` is the only thing that changes state, so applying the patches in order rebuilds the state with
no simulator, no policy engine and no random numbers.

    patch op:  ["s", "a/b/c", value]   set      a list index one past the end appends
               ["d", "a/b/c"]          delete
"""
import gzip
import hashlib
import json

FORMAT = "topak-usecase-trace/1"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def state_hash(state):
    return sha(canonical(state))


def event_hash(ev):
    return sha(canonical({k: v for k, v in ev.items() if k != "hash"}))


def _key(node, k):
    return int(k) if isinstance(node, list) else k


def apply_patch(state, patch):
    for op in patch:
        keys = op[1].split("/")
        node = state
        for k in keys[:-1]:
            node = node[_key(node, k)]
        last = _key(node, keys[-1])
        if op[0] == "s":
            value = json.loads(json.dumps(op[2]))
            if isinstance(node, list) and last == len(node):
                node.append(value)
            else:
                node[last] = value
        else:
            del node[last]


def diff(path, old, new):
    """The smallest patch that turns `old` into `new`, for a value owned by something outside the kernel."""
    if isinstance(old, dict) and isinstance(new, dict):
        ops = []
        for k in sorted(old):
            if k not in new:
                ops.append(["d", f"{path}/{k}"])
        for k in sorted(new):
            if k in old:
                ops += diff(f"{path}/{k}", old[k], new[k])
            else:
                ops.append(["s", f"{path}/{k}", new[k]])
        return ops
    if isinstance(old, list) and isinstance(new, list):
        ops = []
        for i in range(min(len(old), len(new))):
            ops += diff(f"{path}/{i}", old[i], new[i])
        for i in range(len(old), len(new)):
            ops.append(["s", f"{path}/{i}", new[i]])
        for i in range(len(old) - 1, len(new) - 1, -1):
            ops.append(["d", f"{path}/{i}"])
        return ops
    return [] if old == new and type(old) is type(new) else [["s", path, new]]


def write_trace(path, lines):
    with open(path, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for line in lines:
                gz.write(line.encode() + b"\n")


def read_trace(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    return lines[0], lines[1:]
