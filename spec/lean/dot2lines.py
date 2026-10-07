#!/usr/bin/env python3
"""TLC's state graph (`-dump dot`) as lines GraphCheck.lean reads (ADR-0053, Proposed).

    usage: dot2lines.py <graph.dot> > <graph.lines>

One line per item: `I <id>` an initial state, `S <id> <json>` a state, `E <id> <id>` an edge. A state is its
variables as a JSON object, each value in the encoding `crates/topak-core/src/trace.rs` uses: a set is
`{"$s": [...]}`, a function `{"$f": [[k, v], ...]}`, a record an object, a tuple an array; strings, integers and
Booleans as themselves. A function whose domain is strings prints as a record in TLC and is read as one.
"""
import json
import re
import sys

NODE = re.compile(r'^(-?\d+) \[label="')
EDGE = re.compile(r'^(-?\d+) -> (-?\d+) \[')


def unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", '"': '"', "\\": "\\"}.get(n, "\\" + n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def label_of(line, start):
    """The label's text from `start`, up to the closing quote that is not escaped."""
    i = start
    while True:
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == '"':
            return line[start:i], i
        i += 1


TOKEN = re.compile(r'\s*(?:(?P<str>"(?:\\.|[^"\\])*")|(?P<num>-?\d+)|(?P<sym>\|->|:>|@@|<<|>>|[{}\[\](),])|(?P<id>[A-Za-z_][A-Za-z0-9_]*))')


def tokens(s):
    pos, out = 0, []
    while pos < len(s):
        if s[pos:].strip() == "":
            break
        m = TOKEN.match(s, pos)
        if not m:
            raise ValueError(f"cannot read TLA+ value at: {s[pos:pos + 40]!r}")
        pos = m.end()
        if m.group("str") is not None:
            out.append(("str", json.loads(m.group("str"))))
        elif m.group("num") is not None:
            out.append(("num", int(m.group("num"))))
        elif m.group("sym") is not None:
            out.append(("sym", m.group("sym")))
        else:
            out.append(("id", m.group("id")))
    return out


class Parser:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self, kind=None, val=None):
        k, v = self.peek()
        if (kind and k != kind) or (val is not None and v != val):
            raise ValueError(f"expected {kind} {val}, got {k} {v}")
        self.i += 1
        return v

    def value(self):
        k, v = self.peek()
        if k == "str" or k == "num":
            self.i += 1
            return v
        if k == "id":
            self.i += 1
            if v == "TRUE":
                return True
            if v == "FALSE":
                return False
            raise ValueError(f"unexpected identifier {v}")
        if v == "{":
            self.i += 1
            items = self.seq("}")
            return {"$s": items}
        if v == "<<":
            self.i += 1
            return self.seq(">>")
        if v == "[":
            self.i += 1
            rec = {}
            if self.peek()[1] == "]":
                self.i += 1
                return rec
            while True:
                key = self.take()
                self.take("sym", "|->")
                rec[str(key)] = self.value()
                if self.peek()[1] == ",":
                    self.i += 1
                    continue
                self.take("sym", "]")
                return rec
        if v == "(":
            self.i += 1
            pairs = []
            while True:
                key = self.value()
                self.take("sym", ":>")
                pairs.append([key, self.value()])
                if self.peek()[1] == "@@":
                    self.i += 1
                    continue
                self.take("sym", ")")
                return {"$f": pairs}
        raise ValueError(f"unexpected token {k} {v}")

    def seq(self, close):
        items = []
        if self.peek()[1] == close:
            self.i += 1
            return items
        while True:
            items.append(self.value())
            if self.peek()[1] == ",":
                self.i += 1
                continue
            self.take("sym", close)
            return items


def state_of(text):
    """`/\\ x = v` conjuncts as a dict."""
    out = {}
    for part in re.split(r"(?m)^/\\ ", text):
        part = part.strip()
        if not part:
            continue
        name, _, val = part.partition(" = ")
        p = Parser(tokens(val))
        out[name.strip()] = p.value()
        if p.i != len(p.t):
            raise ValueError(f"trailing tokens in {name}")
    return out


def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = EDGE.match(line)
            if m:
                print(f"E {m.group(1)} {m.group(2)}")
                continue
            m = NODE.match(line)
            if m:
                raw, end = label_of(line, m.end())
                st = state_of(unescape(raw))
                print(f"S {m.group(1)} {json.dumps(st, separators=(',', ':'), sort_keys=True)}")
                if "style = filled" in line[end:]:
                    print(f"I {m.group(1)}")


if __name__ == "__main__":
    main()
