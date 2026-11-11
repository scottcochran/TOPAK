# slm/occupant/: the trained SLM as a compiled occupant

**2026.11.11** · scripts and procedures · **not a corpus record**

This directory runs the trained Persona (`runs/full/L-A`) as the occupant that ADR-0036 §3 describes. The
occupant is a fixed Build round: Read, then Draft, then Submit. The Persona writes the drafted content. The
occupant runs inside the reference's launcher at rung 1, on an image that passes P3. It is ADR-0036 §4's
subtraction, applied: a compiled occupant on a `scratch` base.

| File | What it is |
|---|---|
| `src/` | The occupant, in Rust. `bundle.rs` ports `serve.py`'s `load_bundle`. `model.rs` is `model.py`'s llama forward pass in f32. `sample.rs` is `serve.py`'s generate loop. `channel.rs` holds the launcher's guest protocol and the rung-0 `topak mcp` transport |
| `tests/refusal.rs` | A bundle that does not match `model.json` exits 3 with nothing written to stdout |
| `Dockerfile` | A builder pinned by digest, a `--locked` static musl build, then `FROM scratch` with the one binary, `USER 10001:10001` |
| `parity.py` | Checks the trained model as MLX runs it against the occupant: tokenizer ids, logits, 64 greedy tokens |
| `run_rung1.py` | The run: a three-replica cluster, three profiles promoted, the rung-1 round and its refusals, and the rung-0 principal beside it |
| `profile-rung1.json` | The rung-1 profile, written by the last run with the measured image digest |
| `parity-results-2026.11.11.txt`, `../occupant-rung1-results-2026.11.11.txt` | Results |

## What it shows, and what it does not

- **A rung-1 grant on a profile where every clause passes or is vacuous.** The lease's `because` names only the
  criterion. P1, P2, P3, P5, P6 and P7 pass, and P4 is vacuous (no `Invoke`).
- **`Contained` stays false.** The issued rules set no criterion, because ADR-0035 is Proposed and its θ values
  are unset (ADR-0034 §4 A3). The run does not set one.
- **"Asserted by the launcher" means what ADR-0034 §2 says.** The host operator, the launcher, the container
  runtime and Docker Desktop's VM are trusted for the clause verdicts (ADR-0036 §5). Nothing measures or attests
  the image. That would be rung 2 and above.
- **The rules are DEV rules.** The keys are generated per run, and `gates_passed` is an operator request, so
  promotion's gates are asserted, not run.
- **ADR-0036 §7 is not what this shows.** §7 names the Python image of `slm/serve/` with P3 `fail`. That step was
  skipped by the custodian's choice (2026.11.11). See the results file's findings.

## Run it

From `slm/`, with Docker running, the external volume mounted (for `runs/full/L-A`), and
`data/corpora/fineweb-edu-2024-10@full` present:

```sh
cargo test --release --manifest-path occupant/Cargo.toml
docker build --provenance=false -f occupant/Dockerfile -t topak-slm-occupant occupant
.venv/bin/python occupant/parity.py --bundle <dir holding model.json, model.safetensors, tokenizer.json>
python3 occupant/run_rung1.py          # writes ../occupant-rung1-results-<date>.txt and profile-rung1.json
```

`run_rung1.py` builds `topak` (debug), the host occupant and the image itself. It writes nothing under
`mechanism/` or `policies/`. It builds the cluster under `occupant/run/<name>/`, which is git-ignored and holds
DEV keys in the clear, and removes it afterwards unless `--keep` is given.

## The occupant

```text
occupant [--bundle /model] --read <object digest>... [--target notes.md] [--max-new 128] [--temperature 0]
         [--top-k 50] [--seed 0] [--hold-ms 0] [--transport stdio | mcp --topak BIN --socket PATH --token T]
occupant generate | logits | encode | info [--bundle DIR] ...      host checks
```

1. **Bundle check.** Before its first line, the occupant checks `model.json`'s `weights` and `tokenizer` digests and
   the vocabulary size. On any mismatch it exits 3 and writes nothing to stdout.
2. **Hello and lease.** It sends `hello`: `persona` is sha256 of `model.json`, `family` is `family_tag`, `params` is
   `params.total`, and `root` is the lineage root. It answers every `attest` and waits for `granted`.
3. **Read.** It reads each object. The content arrives over the channel, since no corpus is mounted.
4. **Draft.** It continues the read text: the last 16384 characters, then the last `ctx − max_new` tokens, so the
   window never slides. It drafts the continuation.
5. **Submit.** It submits, then answers until `shutdown`.
6. **Output.** Stdout carries protocol lines only. Lines are capped at 8 MiB.

At temperature 0 the output is token-for-token what `serve.py` generates (`parity.py`). A seeded sample is
deterministic, but its random stream is not MLX's.

With `--transport mcp`, the same round runs on the host. The occupant holds the session token and drives
`topak mcp`. That is the rung-0 principal of `../serve/profile-host-rung0.json`. The image holds no `topak`, so
this path cannot run inside it.
