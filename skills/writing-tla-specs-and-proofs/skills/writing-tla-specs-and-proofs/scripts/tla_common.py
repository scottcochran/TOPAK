#!/usr/bin/env python3
"""Shared by the scripts beside it. Not run by itself.

Where a project keeps things, and how each script finds them:

  modules      the spec directory: --dir, else $TLA_SPEC_DIR, else the current directory
  project root the nearest directory at or above the spec directory that holds .git; else the spec directory
  results      --results-dir, else $TLA_RESULTS_DIR, else <spec>/results if that directory exists, else the spec
               directory (results beside the modules)
  checker      $TLA_JAR, else tools/tla2tools.jar in the spec directory or any directory above it up to the root
  checker pin  tools/TLC-PIN found the same way, else the TLC-PIN beside this file (the skill's default)
  prover       $TLAPM, else tools/tlaps-<version>/bin/tlapm found the same way, else tlapm on PATH
  prover pin   tools/TLAPS-PIN found the same way; there is no default, because a release tag can be rebuilt
               upstream under the same name
  project name $TLA_PROJECT, else the root directory's name; it is the first word of every results file

A pin file is `key value` lines, `#` for comments. TLC-PIN: version, jar_sha256, and optionally tlc (the banner TLC
prints) and url. TLAPS-PIN: version, binary_sha256, and optionally commit, platform, backends. A tool whose digest
is not its pin's is refused unless TLC_UNPINNED=1 or TLAPM_UNPINNED=1 is set, and a results file made that way says
so on its Checker: or Prover: line.

Python 3.9 or later, standard library only.
"""
import datetime
import hashlib
import os
import re
import shutil
import signal
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("INVARIANT", "PROPERTY", "DEADLOCK", "SIMULATE")
VERDICTS = ("HOLDS", "COUNTEREXAMPLE", "DEADLOCK", "NO-ERROR-SAMPLED")
ROW_OPTS = ("states", "depth", "num", "seed", "constraint")
STATEMENT = re.compile(r"^(THEOREM|LEMMA|COROLLARY|PROPOSITION)\s+(\w+)\s*==", re.M)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def today():
    return datetime.date.today().strftime("%Y.%m.%d")


def runner_line(*scripts):
    """The Runner: line of a results file: each script that made it, by digest."""
    return "Runner: " + " ".join(f"{os.path.basename(s)} {sha256(s)}" for s in scripts + (os.path.join(HERE, "tla_common.py"),))


class Layout:
    def __init__(self, spec_dir=None, results_dir=None):
        self.spec = os.path.abspath(spec_dir or os.environ.get("TLA_SPEC_DIR") or os.getcwd())
        if not os.path.isdir(self.spec):
            raise SystemExit(f"{self.spec} is not a directory")
        self.root = self.spec
        d = self.spec
        while True:
            if os.path.exists(os.path.join(d, ".git")):
                self.root = d
                break
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        r = results_dir or os.environ.get("TLA_RESULTS_DIR")
        sub = os.path.join(self.spec, "results")
        self.results = os.path.abspath(r) if r else (sub if os.path.isdir(sub) else self.spec)
        self.project = os.environ.get("TLA_PROJECT") or os.path.basename(self.root)

    def rel(self, path):
        """path as a results file prints it: relative to the project root when it is inside it."""
        path = os.path.abspath(path)
        r = os.path.relpath(path, self.root)
        return path if r.startswith("..") else r

    def up(self, *parts):
        """The first existing <d>/<parts> for d from the spec directory up to the root, or None."""
        d = self.spec
        while True:
            p = os.path.join(d, *parts)
            if os.path.exists(p):
                return p
            if d == self.root or os.path.dirname(d) == d:
                return None
            d = os.path.dirname(d)

    def module(self, name):
        return os.path.join(self.spec, name + ".tla")


def read_pin(path):
    out = {}
    for line in read(path).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, _, v = line.partition(" ")
            out[k] = v.strip()
    return out


class Tool:
    """A checker jar or prover binary with the pin it is held to. path is None when the tool was not found."""

    def __init__(self, path, pin, pin_label, key):
        self.path, self.pin, self.pin_label = path, pin or {}, pin_label
        self.sha = sha256(path) if path and os.path.isfile(path) else None
        self.pinned = bool(self.sha) and self.sha == self.pin.get(key)
        self.want = self.pin.get(key)


def find_checker(layout):
    pin_path = layout.up("tools", "TLC-PIN")
    label = layout.rel(pin_path) if pin_path else "the skill's default TLC-PIN"
    jar = os.environ.get("TLA_JAR") or layout.up("tools", "tla2tools.jar")
    return Tool(jar, read_pin(pin_path or os.path.join(HERE, "TLC-PIN")), label, "jar_sha256")


def require_checker(layout):
    c = find_checker(layout)
    if not c.sha:
        raise SystemExit(f"no tla2tools.jar ({c.path or 'tools/tla2tools.jar not found, TLA_JAR not set'}); "
                         "run setup_check.py --fetch-jar, or set TLA_JAR")
    if not c.pinned and not os.environ.get("TLC_UNPINNED"):
        raise SystemExit(f"{c.path} is sha256 {c.sha}, not the {c.want} pinned by {c.pin_label}; "
                         "set TLC_UNPINNED=1 to run it anyway, and the results file will say so")
    return c


def find_prover(layout):
    pin_path = layout.up("tools", "TLAPS-PIN")
    pin = read_pin(pin_path) if pin_path else {}
    label = layout.rel(pin_path) if pin_path else None
    binary = os.environ.get("TLAPM")
    if not binary and pin.get("version"):
        binary = layout.up("tools", f"tlaps-{pin['version']}", "bin", "tlapm")
    if not binary:
        tools = layout.up("tools")
        found = sorted(d for d in os.listdir(tools) if d.startswith("tlaps-")) if tools else []
        found = [os.path.join(tools, d, "bin", "tlapm") for d in found]
        found = [p for p in found if os.path.isfile(p)]
        binary = found[-1] if found else None
    if not binary:
        which = shutil.which("tlapm")
        binary = os.path.realpath(which) if which else None
    return Tool(binary, pin, label, "binary_sha256")


def is_script(path):
    """A wrapper script is not the prover: its digest would name the wrapper."""
    with open(path, "rb") as f:
        return f.read(2) == b"#!"


def require_prover(layout):
    p = find_prover(layout)
    if not p.sha:
        raise SystemExit("no tlapm: set TLAPM to the binary, install it under tools/tlaps-<version>/, or put it on "
                         "PATH (setup_check.py --proofs says what it finds)")
    if is_script(p.path):
        raise SystemExit(f"{p.path} is a wrapper script; set TLAPM to the tlapm binary so the digest printed is the prover's")
    if not p.pinned and not os.environ.get("TLAPM_UNPINNED"):
        why = (f"is sha256 {p.sha}, not the {p.want} pinned by {p.pin_label}" if p.pin_label
               else "has no pin (no tools/TLAPS-PIN; setup_check.py --write-pins records the one installed)")
        raise SystemExit(f"{p.path} {why}; set TLAPM_UNPINNED=1 to run it anyway, and the results file will say so")
    return p


def prover_line(p):
    """The Prover: and Backends: lines of a proof results file."""
    pin = p.pin
    if p.pinned:
        ident = " ".join(x for x in (pin.get("version"), pin.get("commit") and f"commit {pin['commit']}",
                                     pin.get("platform") and f"({pin['platform']})") if x)
        return [f"Prover: tlapm {ident} sha256 {p.sha}"] + ([f"Backends: {pin['backends']}"] if pin.get("backends") else [])
    code, out = run_group([p.path, "--version"], os.getcwd())
    note = f"NOT the pin in {p.pin_label}" if p.pin_label else "no pin"
    return [f"Prover: tlapm {out.strip().splitlines()[-1] if out.strip() else '?'} sha256 {p.sha} ({note})"]


def strip_comments(text):
    """TLA+ text without \\* line comments and (* nested block comments *)."""
    out, depth, i = [], 0, 0
    while i < len(text):
        two = text[i:i + 2]
        if two == "(*":
            depth, i = depth + 1, i + 2
        elif two == "*)" and depth:
            depth, i = depth - 1, i + 2
        elif two == "\\*" and not depth:
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
        else:
            if not depth:
                out.append(text[i])
            i += 1
    return "".join(out)


def module_chain(module, spec_dir, seen=None):
    """module and every module in spec_dir it reaches through EXTENDS or INSTANCE, dependencies first."""
    seen = [] if seen is None else seen
    path = os.path.join(spec_dir, module + ".tla")
    if module in seen or not os.path.exists(path):
        return seen
    text = strip_comments(read(path))
    deps = []
    for m in re.finditer(r"\bEXTENDS\s+(\w+(?:\s*,\s*\w+)*)", text):
        deps += re.split(r"\s*,\s*", m.group(1))
    deps += re.findall(r"\bINSTANCE\s+(\w+)", text)
    for dep in deps:
        if dep != module:
            module_chain(dep, spec_dir, seen)
    seen.append(module)
    return seen


def run_group(cmd, cwd, env=None):
    """Run cmd in its own process group and kill the whole group when it ends.

    tlapm starts backend processes (Z3, Zenon, Isabelle) that can outlive a timeout or tlapm itself; killing the
    group stops them from loading the machine after the run that started them is over.
    """
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         start_new_session=True)
    try:
        out, _ = p.communicate()
    finally:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    return p.returncode, quiet(out or "")


def quiet(out):
    return "\n".join(line for line in out.splitlines() if "JAVA_TOOL_OPTIONS" not in line)


def tlapm_cmd(prover, cache, threads=None):
    cmd = [prover.path, "--cleanfp", "--strict", "--cache-dir", cache]
    return cmd + (["--threads", str(threads)] if threads else [])


def java_version():
    """(major, first line of `java -version`), or None when there is no java."""
    try:
        p = subprocess.run(["java", "-version"], capture_output=True, text=True)
    except OSError:
        return None
    text = quiet(p.stdout + p.stderr)
    m = re.search(r'version "(\d+)(?:\.(\d+))?', text)
    if not m:
        return None
    major = int(m.group(1))
    if major == 1 and m.group(2):
        major = int(m.group(2))
    return major, text.splitlines()[0]


# ---- row lists -------------------------------------------------------------------------------------------------

def parse_rows(path):
    """(meta, rows) of a row list. meta holds the '# key: value' header lines, each key a list."""
    meta = {"module": [], "title": [], "expected": [], "const": [], "cfg": []}
    rows = []
    for n, raw in enumerate(read(path).splitlines(), 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            m = re.match(r"\s*#\s*(module|title|expected|const|cfg):\s?(.*)$", line)
            if m:
                meta[m.group(1)].append(m.group(2).rstrip())
            continue
        f = line.split("#")[0].split()
        if len(f) < 6:
            raise SystemExit(f"{path}:{n}: a row needs name mut spec kind property expected")
        rows.append(make_row(*f[:6], f[6:], where=f"{path}:{n}"))
    if len(meta["module"]) != 1:
        raise SystemExit(f"{path}: exactly one '# module:' line is required")
    names = [r["name"] for r in rows]
    dup = sorted({x for x in names if names.count(x) > 1})
    if dup:
        raise SystemExit(f"{path}: duplicate row names {dup}")
    return meta, rows


def make_row(name, mut, spec, kind, prop, exp, pairs, where="row"):
    if kind not in KINDS:
        raise SystemExit(f"{where}: unknown kind {kind} (one of {', '.join(KINDS)})")
    if exp == "VIOLATED":  # the word some row lists use for a counterexample, or a deadlock on a DEADLOCK row
        exp = "DEADLOCK" if kind == "DEADLOCK" else "COUNTEREXAMPLE"
    if exp not in VERDICTS:
        raise SystemExit(f"{where}: unknown expected verdict {exp} (one of {', '.join(VERDICTS)})")
    if (exp == "DEADLOCK") and kind != "DEADLOCK":
        raise SystemExit(f"{where}: DEADLOCK is the verdict of a DEADLOCK row only")
    if (exp == "NO-ERROR-SAMPLED") != (kind == "SIMULATE") and exp != "COUNTEREXAMPLE":
        raise SystemExit(f"{where}: a SIMULATE row expects NO-ERROR-SAMPLED or COUNTEREXAMPLE, and no other row "
                         "expects NO-ERROR-SAMPLED: a sample is never a check")
    opts, consts = {}, {}
    for kv in pairs:
        if "=" not in kv:
            raise SystemExit(f"{where}: {kv} is not KEY=value")
        k, v = kv.split("=", 1)
        (opts if k in ROW_OPTS else consts)[k] = v
    return dict(name=name, mut=mut, spec=spec, kind=kind, prop=prop, exp=exp, opts=opts, consts=consts)


def default_consts(meta):
    out = []
    for c in meta["const"]:
        if "=" not in c:
            raise SystemExit(f"'# const: {c}' is not NAME = value")
        k, v = c.split("=", 1)
        out.append((k.strip(), v.strip()))
    return out


def classify(row, rc, out):
    """TLC's verdict on one row. Anything that is not exactly one of the verdicts is ERROR, and ERROR is loud."""
    kind, prop = row["kind"], re.escape(row["prop"])
    inv = re.search(rf"^Error: Invariant {prop} is violated", out, re.M)
    if kind == "DEADLOCK" and re.search(r"^Error: Deadlock reached", out, re.M):
        return "DEADLOCK"
    if inv or (kind == "PROPERTY" and re.search(
            rf"^Error: (Temporal properties were violated|Action property {prop} is violated)", out, re.M)):
        return "COUNTEREXAMPLE"
    if rc != 0 or re.search(r"^Error", out, re.M):
        return "ERROR"
    if kind == "SIMULATE":
        return "NO-ERROR-SAMPLED" if re.search(r"Finished in|No error has been found", out) else "ERROR"
    return "HOLDS" if "No error has been found" in out else "ERROR"


def run_row(layout, checker, module, meta, row, workers="1"):
    """Run one row in a temp directory. Returns (verdict, states, as expected?, TLC's output)."""
    tmp = tempfile.mkdtemp(prefix=f"tlc_{row['name']}_")
    try:
        consts = dict(default_consts(meta))
        if row["mut"] != "-":
            consts["Mut"] = f'"{row["mut"]}"'
        for k, v in row["consts"].items():
            consts[k] = v.replace(",", ", ")
        cfg = [f"SPECIFICATION {row['spec']}"]
        if consts:
            cfg += ["CONSTANTS"] + [f"  {k} = {v}" for k, v in consts.items()]
        cfg += meta["cfg"]
        if "constraint" in row["opts"]:
            cfg.append(f"CONSTRAINT {row['opts']['constraint']}")
        cfg.append(("PROPERTY " if row["kind"] == "PROPERTY" else "INVARIANT ") + row["prop"])
        # TLC runs on a copy of the module chain, so the trace files it writes after a counterexample never land
        # in the tree, and with its own java.io.tmpdir, where it unpacks the standard modules: in the shared one a
        # concurrent run can remove them underneath this one.
        for m in module_chain(module, layout.spec):
            shutil.copy(layout.module(m), tmp)
        cfg_path = os.path.join(tmp, "MC.cfg")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("\n".join(cfg) + "\n")
        cmd = ["java", "-XX:+UseParallelGC", f"-Xmx{os.environ.get('TLC_XMX', '2g')}", f"-Djava.io.tmpdir={tmp}",
               "-cp", checker.path, "tlc2.TLC", "-config", cfg_path, "-workers", str(workers),
               "-metadir", os.path.join(tmp, "meta")]
        if row["kind"] != "DEADLOCK":
            cmd.append("-deadlock")
        if row["kind"] == "PROPERTY":
            cmd += ["-fp", "0"]
        if row["kind"] == "SIMULATE":
            o = row["opts"]
            cmd += ["-simulate", f"num={o.get('num', '10000')}", "-depth", o.get("depth", "40"),
                    "-seed", o.get("seed", "1")]
        cmd.append(module + ".tla")
        p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
        out = quiet(p.stdout + p.stderr)
        verdict = classify(row, p.returncode, out)
        pat = r"Progress: ([0-9,]+) states checked" if row["kind"] == "SIMULATE" else r"([0-9,]+) distinct states found"
        m = re.findall(pat, out)
        states = m[-1].replace(",", "") if m else ""
        if row["kind"] == "PROPERTY" and verdict == "COUNTEREXAMPLE" and not re.search(r"\b0 states left on queue", out):
            # TLC checks temporal properties at intervals of the clock, so the count at which it finds a liveness
            # counterexample differs from run to run; printed, it would keep the results file from reproducing.
            states = ""
        ok = verdict == row["exp"] and ("states" not in row["opts"] or states == row["opts"]["states"])
        return verdict, states, ok, out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def count_text(row, verdict, states):
    if states:
        return f"{states} states checked" if row["kind"] == "SIMULATE" else f"{states} distinct states"
    if row["kind"] == "PROPERTY" and verdict == "COUNTEREXAMPLE":
        return "found before the search ended, count not recorded"
    return "no state count"


def format_row(row, verdict, states, ok):
    what = row["prop"] if row["kind"] == "INVARIANT" else f"{row['kind']} {row['prop']}"
    if row["kind"] == "SIMULATE":
        o = row["opts"]
        what += f" (simulate depth={o.get('depth', '40')} traces={o.get('num', '10000')} seed={o.get('seed', '1')})"
    extra = "".join(f" {k}={v}" for k, v in row["consts"].items())
    count = count_text(row, verdict, states)
    mark = "as expected" if ok else f"UNEXPECTED (expected {row['exp']}" + (
        f", states={row['opts']['states']}" if "states" in row["opts"] else "") + ")"
    return f"{row['name']} | Mut={row['mut']} | {row['spec']}{extra} | {what} | {verdict} | {count} | {mark}"


# ---- results files ---------------------------------------------------------------------------------------------

def write_results(layout, stem, date, text):
    """Write <results>/<stem>-<date>.txt and say what happened. A results file is never overwritten: a rerun that
    reproduces it byte for byte says so, and one that differs is written beside it with a letter suffix."""
    os.makedirs(layout.results, exist_ok=True)
    base = os.path.join(layout.results, f"{stem}-{date}")
    for suffix in [""] + list("bcdefghijklmnopqrstuvwxyz"):
        path = f"{base}{suffix}.txt"
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return f"wrote {layout.rel(path)}"
        if read(path) == text:
            return f"reproduced {layout.rel(path)} byte for byte"
    raise SystemExit(f"{base}*.txt: 26 differing results files for one date; look at why the runs do not reproduce")


def newest(layout, pattern):
    import glob
    files = sorted(glob.glob(os.path.join(layout.results, pattern)))
    return files[-1] if files else None
