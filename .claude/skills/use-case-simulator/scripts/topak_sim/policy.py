"""The real evaluators, and the digests that bind a simulation to its configuration."""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import tempfile

ALLOW, VIOL = "topak/bundle/allow", "topak/bundle/violations"
ENGINE_DIR = pathlib.Path(__file__).resolve().parent.parent / "engine"


def opa_path():
    # A shell alias is invisible here, which is the point: the host's Homebrew binary, not a container.
    p = shutil.which("opa") or "/opt/homebrew/bin/opa"
    if not pathlib.Path(p).exists():
        raise SystemExit("opa is required and was not found")
    return p


OPA = opa_path()


def sha_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def bundle_rev(d):
    """mechanism/scripts/build-bundle.sh's revision: SHA-256 over sorted (path NUL bytes NUL)."""
    d = pathlib.Path(d)
    names = sorted(("./" + p.relative_to(d).as_posix()).encode() for p in d.rglob("*")
                   if p.is_file() and ((p.suffix == ".rego" and not p.name.endswith("_test.rego")) or p.name == "data.json"))
    h = hashlib.sha256()
    for n in names:
        h.update(n + b"\0" + (d / n.decode()).read_bytes() + b"\0")
    return h.hexdigest()


def build_engine():
    target = os.environ.get("TOPAK_SIM_TARGET", str(pathlib.Path(tempfile.gettempdir()) / "topak-sim-engine-target"))
    subprocess.run(["cargo", "build", "-q", "--release", "--manifest-path", str(ENGINE_DIR / "Cargo.toml"), "--target-dir", target], check=True)
    return f"{target}/release/topak-sim-engine"


class Engine:
    """Compiled bundles, the linked floor and workflow runs, behind one process."""

    def __init__(self, cfg, bundles):
        self.cfg, self.spec = pathlib.Path(cfg), bundles
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="topak-sim-wasm-"))
        args, self.wasm_sha = [], {}
        for name, b in bundles.items():
            out = self.tmp / f"{name}.tar.gz"
            cmd = [OPA, "build", "-t", "wasm", "--ignore", "*_test.rego", "-o", str(out), str(self.cfg / b["dir"])]
            for e in [ALLOW, VIOL] + b.get("extra_violations", []):
                cmd += ["-e", e]
            subprocess.run(cmd, check=True, capture_output=True)
            d = self.tmp / name
            d.mkdir()
            with tarfile.open(out) as t:
                for m in t.getmembers():
                    base = m.name.lstrip("/")
                    if base in ("policy.wasm", "data.json"):
                        (d / base).write_bytes(t.extractfile(m).read())
            self.wasm_sha[name] = sha_file(d / "policy.wasm")
            args.append(f"{name}={d}/policy.wasm:{d}/data.json")
        self.p = subprocess.Popen([build_engine()] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.calls = 0

    def request(self, obj):
        self.calls += 1
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()
        line = self.p.stdout.readline()
        if not line:
            raise SystemExit("the engine process ended")
        return json.loads(line)

    def bundle(self, name, inp):
        """(allow, violations) for one bundle. An error is a refusal and is reported as one."""
        r = self.request({"b": name, "e": ALLOW, "i": inp})
        if "err" in r:
            return {"bundle": name, "allow": False, "violations": [], "error": r["err"][:200]}
        allow = bool(r["r"] and r["r"][0].get("result") is True)
        rec = {"bundle": name, "allow": allow, "violations": []}
        if not allow:
            vs = []
            for e in [VIOL] + self.spec[name].get("extra_violations", []):
                vr = self.request({"b": name, "e": e, "i": inp})
                if vr.get("r"):
                    vs += vr["r"][0].get("result") or []
            rec["violations"] = sorted(set(vs))
        return rec

    def floor(self, req):
        return self.request({"op": "floor", "req": req})

    def info(self):
        return self.request({"op": "info"})

    def close(self):
        self.p.stdin.close()
        self.p.wait()
        shutil.rmtree(self.tmp, ignore_errors=True)
