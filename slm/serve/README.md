# slm/serve/: run a trained SLM sandboxed in Docker

**2026.09.27** · scripts and procedures · **not a corpus record**

This directory takes a checkpoint from `train.py` (Part A of [`../README.md`](../README.md)) and serves it
from a locked-down container. The container's only channel is stdio. By default it speaks MCP, so an agent
can call the model as a tool. With `--prompt`, it generates once and exits.

**Train on the host and serve in the container.** Docker on macOS runs a Linux VM that cannot use the
Metal GPU, so MLX in a container runs on its CPU backend. That is far too slow for pre-training: a 1M model
trained at about 900 tok/s on a 4-core CPU, against 165k tok/s on the M4 Pro's GPU. It is adequate for
inference at 1–125M parameters. The container runs the same `model.py`, so the architecture needs no
conversion step.

## Build

From `slm/`:

```sh
docker build -f serve/Dockerfile -t topak-slm-serve .
```

- The base image is pinned by its multi-arch digest, and every wheel is installed with `--require-hashes`
  from [`requirements.txt`](requirements.txt). The image is `linux/arm64` on an M-series Mac and
  `linux/amd64` elsewhere.
- `serve/Dockerfile.dockerignore` limits the build context to `model.py`, `serve.py` and
  `requirements.txt`, so `data/` and `runs/` are never sent to the daemon.
- Behind a TLS-intercepting proxy, add `--secret id=pip_ca,src=/path/to/ca.pem`. The CA is used only
  during the install step and is not stored in any layer.

To change a pin, edit `requirements.in` and run the `uv pip compile` command written at its top.

## Run

```sh
# one-shot smoke test
serve/run.sh runs/L-A/ckpt runs/L-A/tokenizer/tokenizer.json --prompt "The history of" --max-new 60

# MCP over stdio (what an MCP client launches)
serve/run.sh runs/L-A/ckpt runs/L-A/tokenizer/tokenizer.json
```

The bundle is three files: `model.json` and `model.safetensors` from the run's output directory, plus
the run's `tokenizer.json`. `run.sh` bind-mounts only those three, read-only.

At startup, the server checks the files against the digests that `model.json` records (`weights`, `tokenizer`).
If any digest differs, it exits with status 3 and serves nothing. To pin the bundle itself, set
`SLM_MODEL_SHA256` to the digest of `model.json`:

```sh
SLM_MODEL_SHA256=$(shasum -a 256 runs/L-A/ckpt/model.json | cut -d' ' -f1) serve/run.sh ...
```

### Sandbox

`run.sh` passes these flags to `docker run`. Change them there, not in the image.

| Flag | Effect |
|---|---|
| `--network none` | No interfaces except loopback. The model cannot fetch or leak anything over the network |
| `--read-only`, `--tmpfs /tmp:noexec,…,size=16m` | Immutable root; the only writable space is a small non-executable tmpfs |
| `--user 10001:10001` | Non-root, matching the image's `slm` user |
| `--cap-drop ALL`, `--security-opt no-new-privileges` | No Linux capabilities, and no setuid escalation |
| `--ipc none`, `--pids-limit 64` | No shared memory with the host, and no fork bombs |
| `--memory`/`--memory-swap` 2g, `--cpus 4` | Resource ceilings (`SLM_MEMORY`, `SLM_CPUS`) |
| bundle mounts `readonly` | The model cannot alter its own weights or tokenizer |
| `--log-driver none` | The daemon keeps no copy of prompts or completions |

Docker's default seccomp and AppArmor profiles stay on. On Docker Desktop, the Linux VM is a further
boundary between the container and macOS. Where gVisor is installed (Linux hosts), `SLM_RUNTIME=runsc`
adds a user-space kernel.

Inside the server, each call is bounded:

- `SLM_MAX_NEW` caps the tokens generated per call (default 512).
- `SLM_MAX_PROMPT_CHARS` caps the prompt length (default 16384 characters).
- Arguments are type-checked and range-checked.
- Unknown arguments are rejected.
- A failed call returns an error result and the server keeps running.

## MCP tools

| Tool | Arguments | Returns |
|---|---|---|
| `generate` | `prompt` (required), `max_new_tokens` (1–`SLM_MAX_NEW`, default 128), `temperature` (0–2, default 0.8; 0 is greedy), `top_k` (default 50; 0 disables it), `seed` (default 0) | The continuation text |
| `model_info` | none | JSON: the digests of `model.json`, the weights and the tokenizer, plus family, parameters, lineage `root`, `ctx` and the token cap |

Generation is deterministic for a given bundle, prompt, arguments and seed.

To register it with Claude Code, add this to `.mcp.json` (use absolute paths):

```json
{
  "mcpServers": {
    "slm": {
      "command": "/abs/path/TOPAK/slm/serve/run.sh",
      "args": ["/abs/path/TOPAK/slm/runs/L-A/ckpt", "/abs/path/TOPAK/slm/runs/L-A/tokenizer/tokenizer.json"],
      "env": {"SLM_MODEL_SHA256": "<digest of model.json>"}
    }
  }
}
```

## Limits

- **CPU only.** There is no KV cache, so each new token recomputes the context window. That is fine at
  this scale; at 125M parameters with long outputs, expect seconds per call.
- **This is a base model.** It continues text; it does not follow instructions. At 1–50M parameters the
  output is fluent-ish at best. The sandbox limits what the model can reach, not what it says.
- **The pin covers the bundle, not the runtime.** The image is pinned by base digest and wheel hashes.
  `serve.py` does not check the image's own digest; pin the image by digest in `SLM_IMAGE` if you need
  that.

## Profile for the host-run occupant (rung 0)

`profile-host-rung0.json` is a confinement profile (ADR-0034 §1, ADR-0036 §1) for running `serve.py` **on the host,
with no container**, as the occupant of a rung-0 lease. Every clause verdict in it is **declared by the operator and
verified by nobody**; a results file that cites it prints `confinement: [digest, 0]` and the word *declared*. It
exists so that the seat records (ADR-0037 to ADR-0039) have a rung-0 principal whose `Mediated` verdict is derived
from a profile rather than from nothing. It is not a step toward the sandbox gap (`mechanism/` G1); the container
and launcher above are. The same profile schema carries the guest up the rungs, and the file's `_ladder` lists the
steps.
