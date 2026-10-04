# slm/: local SLM pre-training, and the ADR-0035 lineage rehearsal

**2026.09.25** · scripts and procedures · **not a corpus record** · sources: `sessions/2026.09.25-SLM.md`,
`decisions/ADR-0035.md` (Proposed)

This directory does two things:

- **Part A** pre-trains small language models from scratch on an Apple-silicon Mac with MLX. It follows the
  session plan: a corpus slice, a 16k BPE tokenizer, `uint16` token shards, a Llama-style decoder, and
  AdamW with warmup and cosine decay, resumable checkpoints, and held-out loss plus samples.
- **Part B** uses that pipeline as ADR-0035 §8's rehearsal. It produces lineage records, runs the E1–E5 +
  distillation gate suite and the monotonicity property check, measures E3 overlap on real corpora, and
  projects one lineage from the reference mechanism's log and cross-checks it against its manifest. Those
  are the four items of the ratification condition.

**What this proves, and what it does not.** It proves the pipeline and the rule's mechanics. It does not
prove the guarantee or seat capability. An M4 is not a confidential VM, and every round here runs at
rung 0, so every record is *declared* (ADR-0035 §2, D-0035-1), including the one projected from the log.
Nothing at 1–50M parameters is a usable Observer. The session says so, and the ADR repeats it (§8).

---

## Layout

| Path | What |
|---|---|
| `pyproject.toml`, `uv.lock` | Python 3.12 environment. `uv.lock` is the version pin (MLX 0.32.2, tokenizers 0.23.2, pyarrow 25.0.1) |
| `corpora.json` | Corpus catalogue: pinned HF revisions and parquet files, plus each corpus's **admission declaration** (`generators`, `generated_share`, `curators`) |
| `prepare_corpus.py` | Step 2: stream a slice into content-addressed JSONL shards + `corpus.json` |
| `train_tokenizer.py`, `pretokenize.py` | Step 3: byte-level BPE; `train.bin`/`val.bin` as `uint16` |
| `model.py` | Step 4: `llama` (`decoder-transformer`) and `ssd` (`ssm`, a Mamba-2-style mixer) families, presets 1m…125m |
| `bench.py` | Step 5: measured tokens/s and TFLOPS per preset, turned into wall-clock budgets |
| `train.py` | Steps 6–7: AdamW, warmup + cosine, bf16 over fp32 master weights, grad accumulation, resumable checkpoints, SIGINT-safe |
| `sample.py` | Step 8: held-out loss and samples |
| `manifest.py` | The authored manifest (the session's shape) and the **declared** lineage record built from it |
| `lineages.json`, `pipeline.py`, `run_long.sh` | The §8 lineages, run end to end; `run_long.sh` adds AC-power check, `caffeinate`, logging, retry |
| `lineage/record.py` | The ADR §1 lineage record: aggregates over the DAG, weakest-link strength |
| `lineage/independence.py` | E1–E5 + distillation over records → independence table (§3–§4) |
| `lineage/gate_suite.py` | Ratification items 1–2: cases, each clause seen to fire alone, and the §2 property check |
| `lineage/overlap.py`, `lineage/measure_pairs.py` | Ratification item 3: exact + MinHash near-duplicate overlap, the E3 measurement tool |
| `lineage/project.py` | Ratification item 4: project a record from the reference's log; cross-check the manifest |
| `lineage/thresholds.example.json` | **Placeholder** θ values. Not floor values |
| `rehearsal/init.py`, `rehearsal/drive.py`, `rehearsal/slm_tool.py` | A three-replica reference cluster whose `Invoke` runs the pipeline as MCP tools, and the author-seat driver |
| `serve/` | Inference for a trained checkpoint in a sandboxed Docker container (no network, read-only, non-root), as an MCP tool over stdio ([README](serve/README.md)) |

Generated data lives in `data/`, `runs/` and `rehearsal/run/`, all git-ignored.

---

## 0. Setup

```sh
cd slm
uv sync                                   # creates .venv from uv.lock
uv run python -c 'import mlx.core as mx; print(mx.default_device())'   # Device(gpu, 0)
```

Part B §B3 also needs the reference mechanism's toolchain (`cargo`, see `mechanism/README.md`) and Docker for
the OPA bundle build.

---

## Part A: pre-training procedure

### A1. Measure before you budget (session step 5)

Training costs about 6 × N × D FLOPs. Get the rate from the machine, not from hope:

```sh
uv run bench.py --budgets 1e9                       # llama presets, 16k vocab
uv run bench.py --family ssd --presets 10m 46m
```

Measured on this machine (M4 Pro, 24 GB, MLX 0.32.2, bf16, micro-batch 16), with optimizer steps included:

| Preset | Params | ctx | tok/s | TFLOPS | Peak mem | Chinchilla (20 tok/param) | 1B tokens |
|---|---|---|---|---|---|---|---|
| `1m` | 1.3M | 256 | 164,740 | 1.31 | 1.6 GB | 25M tok → 3 min | 1.7 h |
| `10m` | 10.6M | 512 | 47,750 | 3.34 | 4.1 GB | 212M → 1.2 h | 5.8 h |
| `30m` | 27.5M | 512 | 21,352 | 3.83 | 5.7 GB | 551M → 7.2 h | 13.0 h |
| `46m` | 46.9M | 1024 | 9,429 | 3.01 | 14.3 GB | 939M → 27.7 h | 29.5 h |
| `ssd 46m` | 44.6M | 1024 | 12,836 | 3.53 | 15.4 GB | 893M → 19.3 h | — |

The session assumed ~1.5 TFLOPS on a base M4 and said an M4 Pro roughly halves the times. The 46M/1B
estimate of 2–3 days on a base M4 becomes 29.5 h here, which is consistent. Small models underuse the GPU, so
the 1M smoke model's rate understates the large presets. **Benchmark the preset you will run.** At 46M, peak
memory is 14 GB, so leave headroom or use `--micro-batch 8`.

Then do the session's smoke test on real data, which checks the whole loop rather than just speed:

```sh
uv run prepare_corpus.py tinystories-a --max-bytes 2e7 --shard-bytes 4e6 --out data/corpora/smoke
uv run train_tokenizer.py --objects data/corpora/smoke/objects --out runs/smoke/tokenizer
uv run pretokenize.py --objects data/corpora/smoke/objects --tokenizer runs/smoke/tokenizer/tokenizer.json --out runs/smoke/tokens
uv run train.py --tokens runs/smoke/tokens --out runs/smoke/ckpt --preset 1m --minutes 10
```

With `--minutes` and no token budget, `train.py` times a few steps first and sizes the LR schedule to fit
the time box. `runs/smoke/ckpt/metrics.jsonl` then holds tokens/s, TFLOPS, train loss and held-out loss.

### A2. Data (session step 2)

```sh
uv run prepare_corpus.py fineweb-edu-2024-10 --max-bytes 4e9          # ≈ 1B tokens
uv run prepare_corpus.py tinystories-a --max-bytes 2e9                # TinyStories, ≈ 470M tokens
```

Sources are pinned by dataset revision and file list in `corpora.json` and streamed over HTTP. A slice
downloads only the row groups it needs. Shards are JSONL named by their SHA-256. That is the reference
mechanism's corpus layout, so a slice can be mounted as a corpus root as it stands. Long documents (PG-19
books) are cut at paragraph breaks into ≤ 50k-character pieces. The same arguments always give the same
objects.

### A3. Tokenizer and pre-tokenization (session step 3)

```sh
uv run train_tokenizer.py --objects data/corpora/fineweb-edu-2024-10/objects --out runs/L-A/tokenizer --vocab 16384
uv run pretokenize.py --objects data/corpora/fineweb-edu-2024-10/objects \
    --tokenizer runs/L-A/tokenizer/tokenizer.json --out runs/L-A/tokens
```

The tokenizer trains on an evenly strided ~500 MB sample, not the head of the corpus. The held-out split is by
a hash of document content, 0.5% by default, so it does not depend on shard order. `meta.json` records the
measured bytes per token: 3.94 on TinyStories.

### A4. Train (session steps 4, 6, 7)

```sh
cat > runs/L-A/train.config.json <<'EOF'
{"tokens": "runs/L-A/tokens", "out": "runs/L-A/ckpt", "seed": 101,
 "model": {"family": "llama", "preset": "46m"}, "tokens_budget": 1000000000}
EOF
caffeinate -dims uv run train.py --config runs/L-A/train.config.json     # re-run to resume
./run_long.sh L-A --profile full        # the same for a lineages.json lineage, with the operator wrapper
```

Defaults are the session's: AdamW β (0.9, 0.95), peak LR 6e-4, 1% warmup, cosine to 10% of peak, weight decay
0.1 on matrices only, clipping at 1.0, bf16 compute over fp32 master weights, and 0.25M tokens per step via
accumulation. Presets: `46m` is the session's d_model 512 × 12 layers × 8 heads, ctx 1024, tied embeddings.

Operating it:

- **Resume** by re-running the same command. A checkpoint (fp32 weights, optimizer state, step) is written every
  30 minutes, on Ctrl-C or SIGTERM, and at the end. Batches are a pure function of (seed, step), so a resumed
  run sees the same data as an unbroken one. The checkpoint records the config's digest and refuses to resume
  under a different config.
- **Time boxes**: `--minutes` (`max_minutes`) bounds one invocation. On a budgeted run that stops early, the resume
  checkpoint is kept and `model.json` says `"complete": false`. Re-running continues, and `pipeline.py` does so
  on its own.
- **Power and heat**: `run_long.sh` refuses to start on battery, wraps the run in `caffeinate -dims`, logs
  `pmset -g therm` every 10 minutes and retries a crashed run up to 5 times. A fanless MacBook Air will throttle
  over multi-day runs.
- **Artifacts**: `init.safetensors` (the from-scratch initialisation; its digest is the lineage `root`),
  `model.safetensors`, `model.json`, `metrics.jsonl`.

### A5. Evaluate (session step 8)

```sh
uv run sample.py runs/full/L-A/ckpt --tokenizer runs/full/L-A/tokenizer/tokenizer.json --tokens runs/full/L-A/tokens \
    --prompt "The history of" -n 3
```

Held-out loss and reading samples are the evaluation at this size. HellaSwag and similar benchmarks sit near
chance.

---

## Part B: the ADR-0035 rehearsal

ADR-0035 §8's ratification condition has four items. Each maps to a command here:

| # | Condition | Command | State |
|---|---|---|---|
| 1 | Gate-suite cases for E1–E5 and distillation, each seen to fire | `lineage/gate_suite.py` | **passes**: every clause fires alone at least once |
| 2 | Property check: adding to ingress, with consumed fixed, never turns a fail into a pass | `lineage/gate_suite.py` | **holds** under ADR-0035 R2 (`bounded`, 2026.09.28). Failed as first drafted (`ratio`). See Finding 1 |
| 3 | E3 overlap measurements, with θ values proposed from them | `lineage/overlap.py`, `measure_pairs.py` | tool ready; first real measurements at 20 MB (§B2). θ needs slices at training size |
| 4 | A lineage projected from the reference's log that matches its manifest | `rehearsal/drive.py` | **done** (§B3), rerun 2026.09.28 under the R2 record schema: honest consistent, three tampers Contested |
| 5 | A best-practice review of the bounded-share construction, by someone other than its author | — | **owed** (ADR-0035 R2, Open obligations) |

**Evidence status (2026.09.25, rerun).** The table's claims are now recorded: the whole of Part B was rerun
the same day and captured to dated results files beside this README — `gate-suite-results-2026.09.25.txt`
(B1: cases pass, monotonicity VIOLATED as written at E3 13/2000 and distillation 241/2000, HOLDS in
`--mode absolute`), `e3-overlap-results-2026.09.25.txt` (B2 at the recorded 20 MB smoke size, ×12 containment
1.00000 at 3,911 of 3,911), `independence-results-2026.09.25.txt` (B4 smoke: exactly the §8 table, 9 of 28
pairs independent), and `rehearsal-results-2026.09.25.txt` (B3: honest round consistent; omit-object, seed
and inject all Contested). Output directories (`data/`, `runs/`, `rehearsal/run/`) remain gitignored; the
results files are the record (09.25 critical review, CR-22).

**2026.09.28, ADR-0035 R2.** Finding 1 below was accepted into the record. The lineage record gained a `consumed`
set (what a round's rounds `Read`), and every share the gate computes is now an upper bound: numerators over
`ingress`, denominator the smaller `consumed` set. `gate-suite-results-2026.09.28.txt` records all three modes:
`bounded` (the ADR) holds over 2,000 trials; `ratio` (as first drafted) still fails at E3 13/2000 and distillation
241/2000; `absolute` (not taken) holds. The suite now also shows the §7 padding residual: a round that also *Reads*
the extra objects dilutes the bound in 24/2000 E3 trials and 250/2000 distillation trials under `bounded`, and 0
under `absolute`. That is declared in the ADR, not fixed.

### B1. Gate suite and property check

```sh
uv run lineage/gate_suite.py                    # bounded, the ADR (R2): cases pass, monotonicity holds (exit 0)
uv run lineage/gate_suite.py --mode ratio       # as first drafted: cases pass, monotonicity VIOLATED (exit 2)
uv run lineage/gate_suite.py --mode absolute    # the candidate not taken: cases pass, property holds
```

The cases use synthetic records that mirror the §8 table, with declarations copied from `corpora.json`. Every
clause fires alone at least once, so no clause passes only because a neighbour caught its case. The suite
also checks that the relation is irreflexive, symmetric and not transitive (L-A⊥L-B and L-B⊥L-D hold, while
L-A⊥L-D fails), that E3 fails closed without a measurement or with an unpinned tool, and weakest-link strength.

### B2. E3 measurements (no training needed)

```sh
for c in fineweb-edu-2024-10 fineweb-2024-10 pg19 fineweb-edu-2023-50; do
  uv run prepare_corpus.py $c --max-bytes 1e9 --out "data/corpora/$c@e3"; done
uv run lineage/overlap.py --a "data/corpora/fineweb-edu-2024-10@e3" --b "data/corpora/fineweb-2024-10@e3" \
    --granularity window:256 --out runs/overlap/edu-vs-web.json
uv run lineage/overlap.py --a "data/corpora/fineweb-edu-2024-10@e3" --b "data/corpora/pg19@e3" \
    --granularity window:256 --out runs/overlap/edu-vs-books.json
uv run lineage/overlap.py --a "data/corpora/fineweb-edu-2024-10@e3" --b "data/corpora/fineweb-edu-2023-50@e3" \
    --granularity window:256 --out runs/overlap/edu24-vs-edu23.json
```

- **Exact** overlap compares a SHA-256 of each normalized unit. **Near** overlap uses MinHash over word 5-grams
  with 112 permutations in 14 bands × 8 rows, which are FineWeb's own dedup parameters. On synthetic edits,
  detection is 1.00 at 1 edit in 300 words, 0.98 at 5, 0.30 at 15 and 0.01 at 30. Unrelated text never
  collided.
- **Granularity** must be one value across all pairs, because the thresholds pin it. Use `window:256` when books
  are involved: a whole book against a web page is not a meaningful unit.
- **The subset relation reproduces on real slices.** FineWeb-Edu's rows are FineWeb's rows after filtering, in the
  same order. So a head slice of a FineWeb-Edu dump file is contained in a FineWeb head slice of the same dump
  about 12× larger. `lineages.json` gives L-C `corpus_scale: 12` for that reason. Equal-size head slices share
  about 11%, roughly FineWeb-Edu's keep rate.
- Per-object results are cached in `runs/overlap-cache/`, keyed by parameters and tool digest.

First measurements (20 MB head slices, the smoke profile, 2026.09.25):

| Pair | Granularity | Exact | Near | Reading |
|---|---|---|---|---|
| FineWeb-Edu 2024-10 vs FineWeb 2024-10, equal size | doc | 0.1115 | 0.1115 | ≈ FineWeb-Edu's keep rate |
| FineWeb-Edu 2024-10 vs FineWeb 2024-10, FineWeb ×12 | doc | **1.0000** | **1.0000** | 3,911 of 3,911 documents contained: the ADR-0017 case |
| FineWeb-Edu 2024-10 vs FineWeb-Edu 2023-50 | window:256 | 0.0020 | 0.0025 | recrawled pages across dumps |
| FineWeb-Edu 2024-10 vs PG-19 | window:256 | 0.0000 | 0.0000 | books and filtered web, disjoint at this size |
| TinyStories part 0 vs part 1 | doc | 0.0019 | 0.0019 | duplicate stories inside TinyStories itself |

These are too small to set θ from. They show the tool separates the cases by orders of magnitude. The θ values
come from reports at the size you train on. `lineage/thresholds.example.json` is a placeholder and says so.

### B3. A lineage projected from the reference's log

```sh
uv run prepare_corpus.py pg19 --max-bytes 8e6 --shard-bytes 1e6 --out "data/corpora/pg19@rehearsal"
uv run rehearsal/init.py --name pg --corpus "data/corpora/pg19@rehearsal"      # cargo + docker
uv run rehearsal/drive.py --name pg --family ssd --minutes 10                  # the honest round
uv run rehearsal/drive.py --name pg --family ssd --minutes 0.5 --tamper omit-object   # also: seed, inject
```

`init.py` builds a separate three-replica cluster under `rehearsal/run/pg/`, leaving `mechanism/dev` and
`policies/` untouched. Its corpus root is the shard set. Its tool allowlist is three MCP tools
(`slm_tokenizer`, `slm_pretokenize`, `slm_pretrain`) served by one generated wrapper. The wrapper embeds a
digest of the pipeline code and refuses to serve if the code has changed, so the reference's binary pin
(mechanism I13) covers what the wrapper imports. Re-run `init.py` after editing any pipeline file. The bundle
is the repository's policies plus an input schema for each tool.

`drive.py` plays the author seat over MCP: `Read` each object, `Draft` it into `corpus/` (checked to be a byte
copy), then `Draft` a config and `Invoke` each tool, then `Submit`. Every parameter is in a drafted config, so
the log carries it as a `Draft` digest and no float is ever digested on both sides. It then writes the author's
`manifest.json` and runs `lineage/project.py` against **replica 2's** archive. Replica 1 decided every action,
so the projection is not taken from the replica that ran the effects.

The projector gets each field from these sources:

- **Ingress**: the corpus root in force (`params.json`, checked against the params digest in every admit). It is
  over-approximated to what the round *could* read, and adds any `Draft` into the tool's data directory that is
  not a byte copy of a `Read` object, charged as generated by the author's Persona (Finding 3).
- **Trainer**: the `slm_pretrain` admit. The config is found by matching the admit's inputs digest against the
  round's drafted paths, and the file is checked against that `Draft`'s digest.
- **Root, weights and tokenizer**: files in the workspace, after checking the workspace digest against the
  `Submit` artifact. The workspace lives only on replica 1 (mechanism G9), so it is the one input not from the
  log.

Result on this machine (8 PG-19 shards, 160 book chunks, 8.1 MB; an `ssd` model of 0.49M parameters with a 4k
vocabulary), rerun 2026.09.28 after ADR-0035 R2 added `consumed` to the record
(`rehearsal-results-2026.09.28.txt`; the 2026.09.25 run is kept beside it):

```text
round    seat a1, lease 1, slots 2–24, every action admitted:
         8 × (Read, Draft copy) · 3 × (Draft config, Invoke) · Submit
train    4,787 steps inside one Invoke (510 s), held-out loss 3.51
record   projected from replica 2's archive, params e06c6116…, rung 0 → strength declared
         ingress 8 objects (8.1 MB, the corpus root) · consumed 8 (8.1 MB, every root object Read) · generated 0 B
check    honest manifest                 consistent
         --tamper omit-object            Contested  corpus object fdd9e085… Read at slot 16, absent from the manifest
         --tamper seed                   Contested  seed claimed 8, projected 7 (slot 23)
         --tamper inject                 Contested  authored Draft 8f5b917c… (slot 18) charged as ingress generated by
                                                    persona:00…, absent from the manifest; consumed 9 = 8 read + 1 authored
```

The honest round reads its whole root, so `consumed` equals `ingress` and the §2 bound is exact for it. The two
sets differ only when a round is charged with root it did not `Read`, which the rehearsal's driver never does.

Each rehearsal is one round on a fresh log, so `drive.py` clears the replicas' state first. Results go to
`rehearsal/run/pg/result-<honest|tamper>/`: the transcript, the manifest, `lineage.projected.json` and
`crosscheck.json`.

### B4. The §8 lineages and the independence table

```sh
uv run pipeline.py L-A L-B L-C L-D L-T L-T2 L-E5 L-A-prime --profile smoke     # minutes each; noise models
./run_long.sh L-A L-B L-C L-D L-T L-T2 L-E5 L-A-prime --profile small          # ~20 min each
uv run lineage/measure_pairs.py "runs/small/*/lineage.json" --granularity window:256 --out runs/small/overlap
uv run lineage/independence.py --records "runs/small/*/lineage.json" --overlaps "runs/small/overlap/*.json" \
    --thresholds lineage/thresholds.example.json --out runs/small/independence-table.json
```

| Lineage | Corpus | Family | Expected against L-A |
|---|---|---|---|
| L-B | PG-19 books | `ssm` | **independent** (the pass pair) |
| L-A-prime | fine-tune of L-A on books | `decoder-transformer` | E1 (also E3, E4) |
| L-C | FineWeb, same dump | `ssm` | E3, and E5 via FineWeb's language-ID curator, which both carry |
| L-D | PG-19 books | `decoder-transformer` | E4 alone |
| L-E5 | FineWeb-Edu, another crawl | `ssm` | E5 (and E3 if recrawled pages overlap: measured) |
| L-T vs L-T2 | TinyStories halves | `llama` / `ssm` | E2; L-T and L-T2 are distillations (rung 1) |

The `smoke` profile run of this whole flow (2026.09.25, 1M parameters, 20 MB per corpus, `window:256`,
placeholder θ) gave exactly the §8 table on real corpora:

```text
L-A ⊥ L-B     independent                the pass pair
L-A ⊥ L-A'    fails E1,E3,E4,E5          same root; the fine-tune reads all of L-A's ingress
L-A ⊥ L-C     fails E3,E5                exact overlap 1.000 of the smaller set (FineWeb-Edu inside FineWeb)
L-A ⊥ L-D     fails E4                   alone
L-A ⊥ L-E5    fails E5                   alone (cross-dump overlap 0.0025 < θ_near)
L-T ⊥ L-T2    fails E2                   alone; both are distillations (rung 1)
9 of 28 pairs independent
```

L-B and L-D also share a tokenizer digest. Both trained their own tokenizer on the same PG-19 slice, and BPE
training is deterministic, so E4 treats the two as one tokenizer, correctly.

Seeds differ per lineage on purpose. Two lineages with the same family, preset, vocabulary and seed start from
byte-identical weights, so they share a `root` and E1 fails them, correctly. The `full` profile is the
session's range (30M parameters, Chinchilla tokens, ~7 h each, ~2.5 days for all eight).

Every record from `manifest.py` is **declared**: it is built from what the author wrote. Only §B3's
record is projected, and at rung 0 it is declared too.

---

## Findings for the corpus

1. **ADR-0035 §2's monotonicity claim did not hold for E3 or the distillation rule as first drafted.** *Accepted
   into the record as ADR-0035 R2 (2026.09.28), which bounds every share: numerators over ingress, denominator the
   smaller consumed set. The `absolute` candidate below was not taken; the padding residual is declared in §7.* Both were
   ratios whose denominator grows with ingress: overlap "as a share of the smaller set", and generated content
   as a share of ingress. Adding non-overlapping, non-generated objects dilutes them. So the over-approximation
   §2 calls conservative (charge the trainer with the whole mounted corpus root) *helps* a pair pass E3, and
   helps a distillation escape the rule. The property check finds counterexamples in 13 of 2,000 random trials
   for E3 and 241 of 2,000 for distillation (seed 35). The smallest E3 case: A holds one object, 376 B, fully
   near-duplicated in B, so the share is 1.0 and E3 fails. Add one unrelated 925 B object to A and the share
   drops to 0.29, so E3 passes. A candidate that is monotone measures matched and generated **bytes** against
   absolute θ (`--mode absolute`). That changes what θ means, so it is the ADR's to decide.
2. **The reference's `canonical_json` is not canonical.** `cedar-policy-core` 4.13 enables serde_json's
   `preserve_order`, so `Digest::of_json` hashes structs in field order and maps in insertion order. The doc
   comment in `topak-core/src/types.rs` says keys are sorted. Replicas agree, because they run the same binary.
   But an external verifier must reproduce field order (the projector does this for the params digest), and an
   `Invoke`'s inputs digest depends on the key order the agent happened to send. This belongs in
   `mechanism/GAPS-AND-ASSUMPTIONS.md` §4.
3. **`Draft` is an ingress channel that the corpus root does not bound.** ADR-0035 §1 defines `ingress` from the
   corpus root and parents. A principal can `Draft` arbitrary text into the workspace and train on it, and that
   text comes from the author, which is a model. The projector charges non-copy drafts into the data directory
   as generated by `persona:<digest>`. The rule it applies (which directories are "data") comes from the tool
   contract. The ADR does not state it.
4. **One binary serving several tools gives them one digest.** Mechanism I13 pins SHA-256(binary ‖ schema), and
   the three SLM tools share both. Their allowlist ids still differ by name, so nothing is confused, but the
   digest alone does not identify a tool.

## Limits

- Rung 0 throughout. The trainer is a native tool and the principal is `Mediated` (ADR-0034 D-0034-3), so
  every record is declared. The rehearsal tests every step except the guarantee.
- A fine-tune through the reference (a DAG with a parent node) is not rehearsed. `Read` resolves only corpus
  objects, and weights are binary, so a parent's weights cannot enter a round. `project.py` refuses
  `init_from`.
- The code pin covers the pipeline's source and `uv.lock`, not the interpreter or installed wheels. Both
  lineages of every pair share MLX on Apple silicon, the §7 "shared training stack" residual.
- `generatedBy` and `curatedBy` are only as good as `corpora.json`'s declarations. Unlabeled model text in web
  crawls is invisible (§7).
