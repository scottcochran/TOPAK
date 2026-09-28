#!/usr/bin/env bash
# Run a trained checkpoint in the sandbox. stdio is the only channel.
#
#   serve/run.sh runs/L-A/ckpt runs/L-A/tokenizer/tokenizer.json                  # MCP over stdio
#   serve/run.sh runs/L-A/ckpt runs/L-A/tokenizer/tokenizer.json --prompt "The"   # one-shot
#
# Only the three bundle files are mounted, read-only. Knobs (environment):
#   SLM_IMAGE (topak-slm-serve)  SLM_MEMORY (2g)  SLM_CPUS (4)
#   SLM_MODEL_SHA256             pin model.json's digest; the container refuses anything else
#   SLM_MAX_NEW (512)            cap on generated tokens per call
#   SLM_RUNTIME                  an OCI runtime such as runsc (gVisor), where installed
set -euo pipefail
if [[ $# -lt 2 ]]; then
  sed -n '2,13p' "$0" >&2
  exit 2
fi
ckpt=$(cd "$1" && pwd)
tokenizer=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
shift 2
for f in "$ckpt/model.json" "$ckpt/model.safetensors" "$tokenizer"; do
  [[ -f $f ]] || { echo "run.sh: no such file: $f" >&2; exit 2; }
done

args=(
  --rm -i
  --network none                   # no sockets beyond loopback
  --read-only                      # immutable root filesystem
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m
  --cap-drop ALL
  --security-opt no-new-privileges
  --user 10001:10001
  --ipc none
  --pids-limit 64
  --memory "${SLM_MEMORY:-2g}" --memory-swap "${SLM_MEMORY:-2g}"
  --cpus "${SLM_CPUS:-4}"
  --log-driver none                # stderr still reaches the caller; nothing is kept by the daemon
  --mount "type=bind,src=$ckpt/model.json,dst=/model/model.json,readonly"
  --mount "type=bind,src=$ckpt/model.safetensors,dst=/model/model.safetensors,readonly"
  --mount "type=bind,src=$tokenizer,dst=/model/tokenizer.json,readonly"
  -e SLM_MODEL_SHA256="${SLM_MODEL_SHA256:-}"
  -e SLM_MAX_NEW="${SLM_MAX_NEW:-512}"
)
[[ -n ${SLM_RUNTIME:-} ]] && args+=(--runtime "$SLM_RUNTIME")
exec docker run "${args[@]}" "${SLM_IMAGE:-topak-slm-serve}" "$@"
