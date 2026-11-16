#!/usr/bin/env python3
"""The trained SLM as a rung-1 occupant on a P3-passing image, with a rung-0 principal beside it.

    python3 slm/occupant/run_rung1.py [--name r1] [--keep]

Builds a three-replica reference cluster under slm/occupant/run/<name>/ (DEV rules, in-memory
transport, the repository's policies as a bundle signed under a dev key), then:

  1. promotes three profiles as one-file workspaces (author round, gates_passed, three grant votes,
     register_profile): the rung-1 profile for the `topak-slm-occupant` image, a copy naming
     another image (refusal 1), and the host-run profile slm/serve/profile-host-rung0.json;
  2. launches the occupant at seat c1 (rung 1) on the rung-1 profile: Read → Draft → Submit with
     the Persona's continuation as the drafted content, and while the lease is live, a second
     process at the agent socket with no token (refusal 3);
  3. refusal 1 (the image is not the profile's), refusal 2 (the bundle in the guest does not match
     model.json), and a launch at a rung-0 seat;
  4. the rung-0 principal: an operator grant at seat h0 naming the host profile at rung 0, the
     same occupant run on the host holding its token, the same round;
  5. writes the results to slm/occupant-rung1-results-<date>.txt and the measured rung-1 profile
     to slm/occupant/profile-rung1.json.

Needs: docker (the image built from slm/occupant/Dockerfile and openpolicyagent/opa for the
bundle), cargo, the L-A checkpoint (slm/runs/full/L-A, on the external volume) and its corpus
(slm/data/corpora/fineweb-edu-2024-10@full). Nothing under mechanism/ or policies/ is written.
The criterion is not set: ADR-0035 is Proposed, so `Contained` has no members at any rung.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import re
import shutil
import socket
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
SLM = HERE.parent
REPO = SLM.parent
MECH = REPO / "mechanism"
TOPAK = MECH / "target" / "debug" / "topak"
OCC_HOST = HERE / "target" / "release" / "occupant"
IMAGE = "topak-slm-occupant"
RUN_DIR = SLM / "runs" / "full" / "L-A"
CORPUS = SLM / "data" / "corpora" / "fineweb-edu-2024-10@full"
HOST_PROFILE = SLM / "serve" / "profile-host-rung0.json"
PORT = 7230
MAX_NEW = 128
TTL = 600_000
HOLD_MS = 8000
BUILD_ALPHABET = ["Read", "Draft", "Submit"]
CRITERION = "ADR-0035's criterion is not in force in the issued rules"

log_lines: list[str] = []


def say(s: str = ""):
    print(s, flush=True)
    log_lines.append(s)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def run(*args, **kw) -> str:
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True, **kw).stdout.strip()


def write_json(p: pathlib.Path, v):
    p.write_text(json.dumps(v, indent=2) + "\n")


def agent_request(sock: pathlib.Path, req: dict) -> dict:
    """One request on the agent socket, as topak-mcp's SocketClient sends it."""
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(str(sock))
    s.sendall((json.dumps(req) + "\n").encode())
    s.shutdown(socket.SHUT_WR)
    buf = b""
    while chunk := s.recv(65536):
        buf += chunk
    s.close()
    return json.loads(buf)


def image_id(ref: str) -> str:
    return run("docker", "image", "inspect", "--format", "{{.Id}}", ref).removeprefix("sha256:")


def rung1_profile(image: str, persona: str) -> str:
    """ADR-0036 §1's schema with §4's subtraction applied: every clause passes or is vacuous."""
    p = {
        "_what": "Confinement profile (ADR-0034 §1, ADR-0036 §1) for the compiled occupant: the trained SLM's "
                 "Persona inside a static binary on an empty image, launched by the reference's launcher at rung 1. "
                 "Written by slm/occupant/run_rung1.py with the measured digests. Not a corpus record.",
        "_rung": 1,
        "_verdicts_are": "ASSERTED by the launcher (ADR-0036 §1 R1, ADR-0034 §2): the launcher applies `launch`, "
                         "appraises `image` and `persona`, and is trusted for the rest along with the host operator, "
                         "the container runtime and Docker Desktop's VM (ADR-0036 §5).",
        "image": image,
        "_image": "docker image inspect --format {{.Id}} topak-slm-occupant, built from slm/occupant/Dockerfile: "
                  "FROM scratch, one statically linked binary at /occupant, USER 10001:10001.",
        "launch": {
            "kind": "docker",
            "network": "none",
            "read_only": True,
            "tmpfs": ["/tmp:noexec,nosuid,size=16m"],
            "user": "10001:10001",
            "cap_drop": ["ALL"],
            "security_opt": ["no-new-privileges"],
            "ipc": "none",
            "pids_limit": 64,
            "mounts": [
                {"dst": "/model/model.json", "mode": "ro"},
                {"dst": "/model/model.safetensors", "mode": "ro"},
                {"dst": "/model/tokenizer.json", "mode": "ro"},
            ],
        },
        "_launch": "Every field is one topak-contain's DockerLaunch applies; the launcher adds --rm -i --network none "
                   "--log-driver none. No memory or CPU limit is listed because the launcher cannot apply one.",
        "channel": {
            "kind": "stdio, line-delimited JSON: topak-contain's guest protocol (hello, attest/evidence, granted, "
                    "op/response, shutdown)",
            "token": "None crosses the channel: the bridge is the session and the guest never holds a token "
                     "(ADR-0036 §2)",
            "stderr": "outward only, to the launcher's log; carries no protocol",
        },
        "persona": {"model_json_sha256": persona},
        "clauses": {
            "P1": {"verdict": "pass", "why": "--network none; stdio is the only I/O the launcher connects. Stderr is "
                                             "outward-only and listed"},
            "P2": {"verdict": "pass", "why": "Read-only root, a 16 MB non-executable tmpfs, and the three bundle files "
                                             "read-only. Nothing else is mounted, not even the workspace: the guest "
                                             "reaches it only through Draft and Read"},
            "P3": {"verdict": "pass", "why": "The image is FROM scratch with one statically linked binary, /occupant, "
                                             "which is the occupant itself: no shell, no interpreter, no package "
                                             "manager, no dynamic loader. Its host-only transport, chosen by the "
                                             "launcher's arguments and never by Persona output, could start a named "
                                             "program, and the image holds none but the occupant"},
            "P4": {"verdict": "vacuous", "why": "The occupant's alphabet has no Invoke"},
            "P5": {"verdict": "pass", "why": "Weights and tokenizer are in the guest and inference runs in the "
                                             "occupant process; both are digest-checked against model.json before "
                                             "the identity line, and model.json's digest is a reference value the "
                                             "launcher appraises"},
            "P6": {"verdict": "pass", "why": "--rm; one launch per grant; the guest is destroyed at round end"},
            "P7": {"verdict": "pass", "why": "The image digest and the model.json digest. Changing either is a new "
                                             "profile"},
        },
        "subtractions": {},
    }
    return json.dumps(p, indent=2) + "\n"


class Mcp:
    """`topak mcp` as a client, as slm/rehearsal/drive.py drives it."""

    def __init__(self, sock, token):
        self.p = subprocess.Popen([str(TOPAK), "mcp", "--socket", str(sock), "--token", token, "--domain", "build"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "slm-occupant-run", "version": "0"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg):
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def rpc(self, method, params):
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("topak mcp closed its stdout")
            m = json.loads(line)
            if m.get("id") == self.n:
                return m

    def call(self, name, args):
        r = self.rpc("tools/call", {"name": name, "arguments": args})
        if "error" in r:
            return False, r["error"]
        res = r["result"]
        text = res["content"][0]["text"]
        try:
            detail = json.loads(text)
        except json.JSONDecodeError:
            detail = text
        return not res.get("isError", False), detail

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


class Cluster:
    def __init__(self, root: pathlib.Path, bundle_rev: str, persona: str):
        self.root, self.bundle, self.persona = root, bundle_rev, persona
        self.rounds: dict[str, int] = {}
        self.nodes: list[subprocess.Popen] = []
        self.logs = []

    def next_round(self, seat: str) -> int:
        self.rounds[seat] = self.rounds.get(seat, 0) + 1
        return self.rounds[seat]

    def op(self, req, node=1) -> dict:
        r = subprocess.run([str(TOPAK), "op", "--socket", str(self.root / f"run/n{node}/operator.sock"),
                            json.dumps(req)], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            raise RuntimeError(f"op {req['op']} failed: {r.stderr.strip()}")
        return json.loads(r.stdout)

    def start(self):
        env = {**os.environ, "RUST_LOG": "info"}
        self.logs = [open(self.root / f"run/n{i}.log", "w") for i in (1, 2, 3)]
        self.nodes = [subprocess.Popen([str(TOPAK), "node", "--config", str(self.root / f"n{i}.json")],
                                       stdout=self.logs[i - 1], stderr=self.logs[i - 1], cwd=self.root, env=env)
                      for i in (1, 2, 3)]
        for _ in range(200):
            if all((self.root / f"run/n{i}/operator.sock").exists() for i in (1, 2, 3)):
                break
            if any(p.poll() is not None for p in self.nodes):
                raise SystemExit(f"a replica exited; see {self.root}/run/n*.log")
            time.sleep(0.1)
        time.sleep(2.0)  # leader election

    def stop(self):
        for p in self.nodes:
            p.terminate()
        for p in self.nodes:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
        for f in self.logs:
            f.close()

    def status(self, node=1) -> dict:
        return self.op({"op": "status"}, node)

    def grant(self, principal, seat, alphabet, role="author", confinement=None, persona=None) -> dict:
        return self.op({"op": "grant", "principal": principal, "seat": seat, "persona": persona or "00" * 32,
                        "bundle": self.bundle, "confinement": confinement or {"digest": "00" * 32, "rung": 0},
                        "alphabet": alphabet, "ttl_ms": TTL, "round": self.next_round(seat), "role": role})

    def promote(self, text: str, label: str, profile_file: pathlib.Path) -> str:
        """ADR-0034 §1, ADR-0036 R4: the profile as an authoring round's only file, the gates, three
        grant votes, then register_profile. Returns the file's digest."""
        profile_file.write_text(text)
        pd = json.loads(run(TOPAK, "profile-digest", profile_file))
        assert not pd["malformed"], pd
        g = self.grant(f"author-{label}", "a1", ["Draft", "Submit"])
        assert g.get("ok"), g
        m = Mcp(self.root / "run/n1/agent.sock", g["token"])
        ok, d = m.call("draft", {"target": "profile.json", "content": text})
        assert ok, d
        ok, d = m.call("submit", {})
        assert ok, d
        m.close()
        artifact = d["result"]["submitted"]
        assert artifact == pd["artifact"], f"the round's workspace is not the profile alone: {artifact} {pd}"
        evidence = sha_bytes(f"gates for {label}".encode())
        r = self.op({"op": "gates_passed", "artifact": artifact, "evidence": evidence})
        assert r.get("ok", True), r
        for gs in ("g1", "g2", "g3"):
            v = self.grant(f"voter-{gs}-{label}", gs, ["Vote"], role="voter")
            assert v.get("ok"), v
            m = Mcp(self.root / "run/n1/agent.sock", v["token"])
            ok, d = m.call("vote", {"verdict": "grant", "artifact": artifact, "evidence": evidence, "rules_epoch": 0})
            assert ok, d
            m.close()
        time.sleep(0.5)
        r = self.op({"op": "register_profile", "profile": text})
        assert r.get("ok"), f"register_profile {label}: {r}"
        assert pd["profile"] == sha_bytes(text.encode())
        say(f"  promoted and registered {label:<12} profile {pd['profile']}  (artifact {pd['artifact'][:16]}…)")
        return pd["profile"]

    def launch(self, principal, seat, profile) -> dict:
        return self.op({"op": "launch", "principal": principal, "seat": seat, "profile": profile,
                        "bundle": self.bundle, "alphabet": BUILD_ALPHABET, "ttl_ms": TTL,
                        "round": self.next_round(seat), "role": "author"})

    def until(self, what: str, pred, secs=120):
        t0 = time.time()
        while time.time() - t0 < secs:
            if pred():
                return
            time.sleep(0.25)
        raise SystemExit(f"timed out waiting for {what}")


def setup(root: pathlib.Path, staged: pathlib.Path, obj: str) -> tuple[str, dict]:
    """Keys, DEV rules, params, a signed bundle and three node configs with the launcher."""
    (root / "secrets").mkdir()
    (root / "bundles").mkdir()

    def key(name):
        out = run(TOPAK, "keygen")
        (root / "secrets" / f"{name}.json").write_text(out + "\n")
        return json.loads(out)

    bundle_key = key("bundle")
    env = {**os.environ, "TOPAK_BUNDLE_SECRET": bundle_key["secret"]}
    rev = subprocess.run([str(MECH / "scripts/build-bundle.sh"), str(REPO / "policies"), str(root / "bundles")],
                         check=True, capture_output=True, text=True, env=env).stdout.strip().splitlines()[-1]

    def seat(kind, rung=0):
        d = {"domain": "build", "kind": kind, "key": key(f"seat-{kind}-{len(seats)}")["public"]}
        if rung:
            d["rung"] = rung
        return d

    seats: dict = {}
    for s, kind, rung in (("a1", "thinker", 0), ("h0", "thinker", 0), ("c1", "thinker", 1),
                          ("g1", "grant", 0), ("g2", "grant", 0), ("g3", "grant", 0), ("o1", "observer", 0)):
        seats[s] = seat(kind, rung)
    # The profile author's cell Observer: promotion counts only a covered round (ADR-0024 A2.3,
    # ADR-0039 §3), as in topak-node/tests/contain.rs's fixture.
    seats["o1"]["cell"] = "a1"
    persona = sha_file(staged / "model.json")
    rules = {
        "rules_epoch": 0, "quorum": "all", "min_grant": 2,
        "seats": seats,
        "grant_roster": ["g1", "g2", "g3"], "veto_roster": [],
        "anchor_keys": [key(f"anchor-{i}")["public"] for i in (1, 2, 3)],
        "break_glass": None, "erasure_roster": None,
        "verifier_keys": [], "bundle_keys": [bundle_key["public"]],
        # ADR-0017's provenance axis: L-A was pretrained from scratch in the rehearsal (slm/README.md Part B).
        "personas": {persona: "in_house_pretrain"},
        # No "criterion": ADR-0035 is Proposed and its θ values are unset (ADR-0034 §4 A3).
    }
    write_json(root / "rules.json", rules)
    run(TOPAK, "check-rules", root / "rules.json")
    write_json(root / "params.json", {
        "corpus": [obj], "build_tools": [], "run_tools": [], "run_root": [], "round_bound": 200,
        "run_round_bound": 64, "lease_margin_ms": 500, "after_topic_limit": 64,
    })
    mounts = {f"/model/{n}": str(staged / n) for n in ("model.json", "model.safetensors", "tokenizer.json")}
    args = ["--read", obj, "--max-new", str(MAX_NEW), "--temperature", "0", "--hold-ms", str(HOLD_MS)]
    for i in (1, 2, 3):
        write_json(root / f"n{i}.json", {
            "id": i,
            "peers": {str(j): f"127.0.0.1:{PORT + j}" for j in (1, 2, 3)},
            "data_dir": f"run/n{i}", "agent_socket": f"run/n{i}/agent.sock",
            "operator_socket": f"run/n{i}/operator.sock",
            "rules": "rules.json", "params": "params.json", "corpus_dir": "corpus", "bundles_dir": "bundles",
            "opa_sidecar": None, "kafka": None, "tools": {},
            "contain": {"backends": {"1": {"kind": "docker", "image_ref": IMAGE, "args": args, "mounts": mounts}},
                        "hello_timeout_ms": 10_000},
        })
    return rev, rules


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="r1", help="short name; socket paths must stay under 104 bytes")
    ap.add_argument("--keep", action="store_true", help="leave the cluster directory in place")
    a = ap.parse_args()
    date = time.strftime("%Y.%m.%d")
    root = HERE / "run" / a.name
    if len(str(root / "run/n1/operator.sock")) > 100:
        sys.exit(f"{root} is too deep for a unix socket path; use a shorter --name")
    for p in (RUN_DIR / "ckpt/model.json", RUN_DIR / "ckpt/model.safetensors", RUN_DIR / "tokenizer/tokenizer.json"):
        if not p.exists():
            sys.exit(f"{p} missing: is the external volume mounted?")

    say(f"# The trained SLM as a rung-1 occupant on a P3-passing image · {date}")
    say()
    say("Produced by slm/occupant/run_rung1.py. DEV rules, not genesis rules: keys are generated per run and")
    say("their secrets are in the clear; gates_passed is an operator request, so the gates are asserted, not run.")
    say("ADR-0035 is Proposed and the issued rules set no criterion, so no principal here is Contained.")
    say()

    say("## Build")
    subprocess.run(["cargo", "build", "-q", "--manifest-path", str(MECH / "Cargo.toml"), "-p", "topak-node"], check=True)
    subprocess.run(["cargo", "build", "-q", "--release", "--manifest-path", str(HERE / "Cargo.toml")], check=True)
    subprocess.run(["docker", "build", "-q", "--provenance=false", "-f", str(HERE / "Dockerfile"), "-t", IMAGE, str(HERE)], check=True,
                   capture_output=True)
    image = image_id(IMAGE)
    head = run("git", "-C", REPO, "rev-parse", "HEAD")
    dirty = run("git", "-C", REPO, "status", "--porcelain", "--", "slm/occupant", "slm/serve", "mechanism", "policies")
    say(f"  repository HEAD     {head}{'  (working tree differs under slm/ — see git status)' if dirty else ''}")
    say(f"  topak               {sha_file(TOPAK)}  ({TOPAK.relative_to(REPO)})")
    say(f"  image {IMAGE}  {image}")
    say(f"  host occupant       {sha_file(OCC_HOST)}  ({OCC_HOST.relative_to(REPO)}, {platform.machine()} {platform.system()})")
    say(f"  Cargo.lock          {sha_file(HERE / 'Cargo.lock')}")
    say(f"  docker              {run('docker', 'version', '--format', '{{.Server.Version}} {{.Server.Os}}/{{.Server.Arch}}')}")
    say()

    say("## P3: what the image holds")
    probe = subprocess.run(["docker", "run", "--rm", "--entrypoint", "/bin/sh", IMAGE, "-c", "true"],
                           capture_output=True, text=True)
    sh_msg = probe.stderr.strip().splitlines()[0] if probe.stderr.strip() else ""
    assert probe.returncode != 0 and "/bin/sh" in sh_msg, "the image has a shell"
    say(f"  docker run --entrypoint /bin/sh → exit {probe.returncode}: {sh_msg[-110:]}")
    cid = run("docker", "create", IMAGE)
    try:
        listing = subprocess.run(f"docker export {cid} | tar -tvf -", shell=True, check=True, capture_output=True,
                                 text=True).stdout.splitlines()
    finally:
        run("docker", "rm", cid)
    files = [l for l in listing if l.startswith("-")]
    regular = [l.split()[-1] for l in files if l.split()[4] != "0"]
    say(f"  docker export: {len(listing)} entries; regular files with content: {regular}")
    say("  (the others are empty files and directories the runtime creates: .dockerenv, /dev, /etc/hosts, /proc, /sys)")
    assert regular == ["occupant"], listing
    say()

    # Stage the bundle and the corpus object.
    shutil.rmtree(root, ignore_errors=True)
    (root / "run").mkdir(parents=True)
    (root / "corpus").mkdir()
    staged = root / "model"
    staged.mkdir()
    shutil.copyfile(RUN_DIR / "ckpt/model.json", staged / "model.json")
    shutil.copyfile(RUN_DIR / "ckpt/model.safetensors", staged / "model.safetensors")
    shutil.copyfile(RUN_DIR / "tokenizer/tokenizer.json", staged / "tokenizer.json")
    persona = sha_file(staged / "model.json")
    manifest = json.loads((RUN_DIR / "manifest.json").read_text())
    shard = manifest["corpus"][0]["objects"][0]["digest"]
    with open(CORPUS / "objects" / shard) as f:
        doc = json.loads(f.readline())
    text = doc["text"].encode()
    obj = sha_bytes(text)
    (root / "corpus" / obj).write_bytes(text)

    say("## Inputs")
    say(f"  Persona model.json  {persona}  (slm/runs/full/L-A/ckpt; weights {json.loads((staged / 'model.json').read_text())['weights'][:16]}…)")
    say(f"  corpus object       {obj}  ({len(text)} bytes: the text of document {doc['id']},")
    say(f"                      the first line of L-A corpus shard {shard[:16]}…)")

    rev, rules = setup(root, staged, obj)
    say(f"  bundle revision     {rev}  (repository policies/, signed under a dev key)")
    say(f"  seats               " + ", ".join(f"{s} {d['kind']} rung {d.get('rung', 0)}" for s, d in rules["seats"].items()))
    say(f"  personas            {persona[:16]}… in_house_pretrain;  criterion: not set")
    say()

    # What the honest round should draft: the same binary's continuation on the host.
    gen = json.loads(run(OCC_HOST, "generate", "--bundle", staged, "--prompt-file", root / "corpus" / obj,
                         "--max-new", MAX_NEW, "--temperature", 0))
    expected = gen["text"]

    c = Cluster(root, rev, persona)
    c.start()
    results: dict = {}
    try:
        say("## Profiles promoted")
        p1_text = rung1_profile(image, persona)
        p1 = c.promote(p1_text, "rung-1", root / "profile-rung1.json")
        other = image_id("topak-slm-serve") if subprocess.run(["docker", "image", "inspect", "topak-slm-serve"],
                                                              capture_output=True).returncode == 0 else sha_bytes(b"another image")
        pw = c.promote(rung1_profile(other, persona), "other-image", root / "profile-other-image.json")
        h0_text = HOST_PROFILE.read_text()
        h0 = c.promote(h0_text, "host-rung0", root / "profile-host-rung0.json")
        say()

        say("## Rung 1: the honest round (ADR-0036 §7)")
        t0 = time.time()
        r = c.launch("occupant-1", "c1", p1)
        say(f"  launch c1 → ok={r.get('ok')} verdict={r.get('verdict')} rung={r.get('rung')} fence={r.get('fence')} "
            f"({time.time() - t0:.1f} s to grant)")
        say(f"  token in the reply: {'token' in r};  instance {r.get('instance')}")
        say(f"  contained={r.get('contained')} because={json.dumps(r.get('because'))}")
        results["honest"] = r
        assert r.get("ok") and r.get("verdict") == "attested" and r.get("rung") == 1, r
        assert "token" not in r
        assert r.get("contained") is False and r.get("because") == [CRITERION], r
        fence = r["fence"]
        lease = r["lease"]
        say(f"  lease confinement {json.dumps(lease['confinement'])}, persona {lease['persona'][:16]}…, "
            f"alphabet {lease['alphabet']}")

        # Refusal 3 while the lease is live: a second process at the agent socket, no token.
        c.until("the occupant's Draft", lambda: any(l["seat"] == "c1" and l["actions"] >= 2
                                                     for l in c.status()["live_leases"]), 60)
        say(f"  live at seat c1: {[l for l in c.status()['live_leases'] if l['seat'] == 'c1'][0]['actions']} actions so far")
        # The agent socket's own protocol, one AgentRequest line per connection, so that what refuses
        # is the mechanism and not a client that gives up early (`topak mcp` exits at its tool list).
        for label, tok in (("no token", ""), ("a made-up token", sha_bytes(b"not a token"))):
            for opname, op in (("Read", {"op": "act", "action": {"kind": "Read", "object": obj}}),
                               ("Submit", {"op": "submit_workspace"})):
                r = agent_request(root / "run/n1/agent.sock", {"token": tok, **op})  # AgentRequest flattens its op
                say(f"  refusal 3, a second process with {label}, {opname}: admitted={r.get('admitted')} "
                    f"{json.dumps(r.get('detail'))[:120]}")
                assert r.get("admitted") is False and "UnknownLease" in json.dumps(r.get("detail")), r
        assert any(l["seat"] == "c1" for l in c.status()["live_leases"]), "the occupant's lease is still live"

        c.until("the occupant's Submit", lambda: not any(l["seat"] == "c1" for l in c.status()["live_leases"]))
        c.until("the guest destroyed", lambda: c.status()["launched"] == [], 30)
        say(f"  round over in {time.time() - t0:.1f} s; launched guests now: {c.status()['launched']}")
        cands = []
        for n in (1, 2, 3):
            st = c.status(n)
            cands.append([x for x in st["candidates"] if x["author"] == "c1"])
        say(f"  candidate authored by c1, per replica: {[ [x['artifact'][:16] for x in cs] for cs in cands]}")
        assert all(len(cs) == 1 and cs[0]["artifact"] == cands[0][0]["artifact"] for cs in cands), cands
        drafted = sorted(root.glob("run/n*/workspaces/ws-c1-*/notes.md"))
        assert drafted, "no drafted notes.md in any workspace"
        got = drafted[0].read_text()
        say(f"  drafted {drafted[0].relative_to(root)} ({len(got.encode())} bytes, sha256 {sha_bytes(got.encode())[:16]}…)")
        say(f"  equals the host occupant's greedy continuation of the same object: {got == expected}")
        assert got == expected
        say(f"  drafted text: {json.dumps(got)[:300]}…")
        plain = re.sub(r"\x1b\[[0-9;]*m", "", (root / "run/n1.log").read_text())
        guest_log = [l.rstrip() for l in plain.splitlines() if "guest" in l and "occupant:" in l]
        say("  the guest's stderr, from the launcher's log:")
        for l in guest_log:
            say(f"    {l[l.find('occupant:'):][:160]}")
        say()

        say("## Rung 1: refusals")
        r = c.launch("occupant-2", "c1", pw)
        say(f"  refusal 1, image not the profile's: verdict={r.get('verdict')} reason={json.dumps(r.get('reason'))[:160]}")
        assert r.get("verdict") == "unattestable" and "image" in r.get("reason", ""), r
        assert not any(l["seat"] == "c1" for l in c.status()["live_leases"]) and c.status()["launched"] == []
        results["refusal_image"] = r

        good = staged / "model.safetensors"
        keep = root / "model.safetensors.good"
        shutil.copyfile(good, keep)
        b = bytearray(good.read_bytes())
        b[-1] ^= 0x01
        good.write_bytes(bytes(b))
        try:
            r = c.launch("occupant-3", "c1", p1)
        finally:
            shutil.copyfile(keep, good)
            keep.unlink()
        say(f"  refusal 2, bundle in the guest ≠ model.json (one bit of model.safetensors flipped): "
            f"verdict={r.get('verdict')} reason={json.dumps(r.get('reason'))[:120]}")
        assert r.get("verdict") == "unattestable" and "closed" in r.get("reason", ""), r
        assert not any(l["seat"] == "c1" for l in c.status()["live_leases"])
        results["refusal_bundle"] = r
        say(f"  refusal 3, a second process with no token: shown above, during the live lease")

        r = c.launch("occupant-4", "h0", p1)
        say(f"  a launch at rung-0 seat h0: ok={r.get('ok')} reason={json.dumps(r.get('reason'))[:120]}")
        assert "rung 0" in r.get("reason", ""), r
        say()

        say("## Rung 0 beside it: the host-run occupant")
        g = c.grant("host-occupant", "h0", BUILD_ALPHABET, confinement={"digest": h0, "rung": 0}, persona=persona)
        assert g.get("ok"), g
        say(f"  grant h0 → fence {g.get('fence')}, confinement [{h0[:16]}…, 0], token held by the occupant process")
        hf = g["fence"]
        st = [l for l in c.status()["live_leases"] if l["fence"] == hf][0]
        say(f"  contained={st['contained']['contained']} because={json.dumps(st['contained']['because'])}")
        results["rung0"] = st
        assert st["contained"]["contained"] is False
        assert any("rung 0" in b for b in st["contained"]["because"])
        assert any("P3" in b for b in st["contained"]["because"])
        hr = subprocess.run([str(OCC_HOST), "--transport", "mcp", "--topak", str(TOPAK), "--socket",
                             str(root / "run/n1/agent.sock"), "--token", g["token"], "--bundle", str(staged),
                             "--read", obj, "--max-new", str(MAX_NEW), "--temperature", "0",
                             # Another file name: the same bytes at the same path would be the rung-1
                             # round's artifact, which is already submitted.
                             "--target", "host-notes.md"],
                            capture_output=True, text=True, timeout=300)
        say(f"  host occupant exit {hr.returncode}; its stderr:")
        for l in hr.stderr.strip().splitlines():
            say(f"    {l[:160]}")
        assert hr.returncode == 0, hr.stderr
        c.until("the host occupant's Submit", lambda: not any(l["seat"] == "h0" for l in c.status()["live_leases"]), 30)
        hd = sorted(root.glob("run/n*/workspaces/ws-h0-*/host-notes.md"))
        assert hd and hd[0].read_text() == expected
        say(f"  drafted {hd[0].relative_to(root)}: the same bytes as the rung-1 round's draft: {hd[0].read_text() == got}")
        say()
    finally:
        c.stop()

    say("## The two verdicts, side by side")
    say(f"  rung 1  [{p1[:16]}…, 1]  asserted by the launcher   because: {json.dumps(results['honest']['because'])}")
    say(f"  rung 0  [{h0[:16]}…, 0]  declared, verified by nobody   because: {json.dumps(results['rung0']['contained']['because'])}")
    say("  At rung 1 the only conjunct missing is the criterion; P3 holds. At rung 0 the principal is Mediated by the")
    say("  rung and by its profile's declared P3 failure.")
    say()
    say("## The rung-0 profile's clauses, as declared")
    say(f"  profile {h0} — confinement [{h0[:16]}…, 0]. Every verdict below is DECLARED by the operator and verified by")
    say("  nobody. No participant is trusted for the profile's truth.")
    for k, v in json.loads(h0_text)["clauses"].items():
        say(f"    {k} {v['verdict']:<8} (declared)  {v['why'][:100]}")
    say()
    say("## The rung-1 profile's clauses, as asserted by the launcher")
    say(f"  profile {p1} — confinement [{p1[:16]}…, 1]")
    for k, v in json.loads(p1_text)["clauses"].items():
        say(f"    {k} {v['verdict']:<8} (asserted)  {v['why'][:100]}")
    say()
    say("## Findings")
    for f in FINDINGS:
        say(f"  - {f}")
    say()
    say("RESULT PASS")

    (HERE / "profile-rung1.json").write_text(p1_text)
    out = SLM / f"occupant-rung1-results-{date}.txt"
    out.write_text("\n".join(log_lines) + "\n")
    print(f"\nwrote {out.relative_to(REPO)} and {(HERE / 'profile-rung1.json').relative_to(REPO)}")
    if not a.keep:
        shutil.rmtree(root, ignore_errors=True)


FINDINGS = [
    "Same digest. ADR-0036 R1 has elevation name the same profile digest at a higher rung, one change at a time. "
    "The host-run rung-0 profile and the rung-1 profile are different files (image, launch, channel, P1, P2, P3), so "
    "the step from one to the other changes clause verdicts and the rung together. The profile's _ladder note glosses this.",
    "Resource limits. topak-contain's DockerLaunch applies no --memory, --cpus or environment, so the rung-1 profile "
    "lists none and slm/serve/run.sh's 2 GB / 4 CPU ceilings do not apply under the launcher. Unknown keys in a "
    "profile's launch part are ignored silently (no deny_unknown_fields).",
    "§4 skipped. ADR-0036 §4 and §7 name slm/serve's Python image with P3 fail. This run used a P3-passing image "
    "instead, by the custodian's choice (2026.11.11); §7 as written is therefore not what this run shows.",
    "Stale text under mechanism/. GAPS-AND-ASSUMPTIONS.md G1 ('the only image is P3-fail') and the line saying every "
    "lease is rung 0 no longer describe what the reference can launch. Editing them is a mechanism/ change.",
    "Image identity. The profile's image is docker image inspect's Id. Under Docker Desktop's containerd store that "
    "is the image index digest, and by default the index carries a build-provenance attestation that changes on every "
    "build, so a rebuild of the same binary was a new profile. The image is built with --provenance=false, which made "
    "the Id stable across rebuilds here; it is still not a reproducible-build claim.",
]


if __name__ == "__main__":
    main()
