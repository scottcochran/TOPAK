"""Step 4: two model families, in MLX.

`llama` (family tag `decoder-transformer`): pre-norm decoder with RMSNorm, RoPE, SwiGLU, no
biases and tied input/output embeddings. The layout follows `mlx-lm`'s Llama; the code here is
self-contained so its bytes are part of the trainer's code digest.

`ssd` (family tag `ssm`): the same residual stack with the attention mixer replaced by a
Mamba-2-style selective state-space mixer (SSD: scalar decay per head, state size N, input and
output projections B_t and C_t), computed in chunks with matmuls. It omits Mamba-2's short
causal convolution and keeps a SwiGLU MLP per block, so a block costs about 11d² parameters
against the transformer's 12d². It exists so that ADR-0035's E4 has a second architecture to
compare with. It is not a reference Mamba implementation.

Presets size both families alike. With a 16k vocabulary, the embedding table dominates the
small presets.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_unflatten

FAMILY_TAGS = {"llama": "decoder-transformer", "ssd": "ssm"}

PRESETS = {
    "1m": dict(d_model=64, n_layers=4, n_heads=4, ctx=256),
    "10m": dict(d_model=256, n_layers=8, n_heads=4, ctx=512),
    "30m": dict(d_model=384, n_layers=12, n_heads=6, ctx=512),
    "46m": dict(d_model=512, n_layers=12, n_heads=8, ctx=1024),
    "125m": dict(d_model=768, n_layers=16, n_heads=12, ctx=1024),
}


@dataclass
class ModelConfig:
    family: str = "llama"
    vocab_size: int = 16384
    d_model: int = 512
    n_layers: int = 12
    n_heads: int = 8
    ctx: int = 1024
    ffn_hidden: int = 0  # 0: 8/3·d rounded up to a multiple of 64
    rope_base: int = 10000
    norm_eps_e6: int = 10  # 1e-5, stored as an integer so configs digest identically everywhere
    ssm_state: int = 64
    ssm_chunk: int = 64

    def __post_init__(self):
        assert self.family in FAMILY_TAGS, f"family must be one of {list(FAMILY_TAGS)}"
        assert self.d_model % self.n_heads == 0
        if not self.ffn_hidden:
            self.ffn_hidden = 64 * math.ceil(self.d_model * 8 / 3 / 64)

    @property
    def eps(self) -> float:
        return self.norm_eps_e6 * 1e-6

    @property
    def family_tag(self) -> str:
        return FAMILY_TAGS[self.family]

    @classmethod
    def from_preset(cls, preset: str, **kw) -> "ModelConfig":
        return cls(**{**PRESETS[preset], **kw})

    def to_dict(self) -> dict:
        return asdict(self)


class Attention(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.h, self.hd = c.n_heads, c.d_model // c.n_heads
        self.qkv = nn.Linear(c.d_model, 3 * c.d_model, bias=False)
        self.o_proj = nn.Linear(c.d_model, c.d_model, bias=False)
        self.rope = nn.RoPE(self.hd, traditional=False, base=c.rope_base)

    def __call__(self, x):
        B, T, D = x.shape
        q, k, v = mx.split(self.qkv(x), 3, axis=-1)
        q, k, v = (t.reshape(B, T, self.h, self.hd).transpose(0, 2, 1, 3) for t in (q, k, v))
        q, k = self.rope(q), self.rope(k)
        o = mx.fast.scaled_dot_product_attention(q, k, v, scale=self.hd ** -0.5, mask="causal")
        return self.o_proj(o.transpose(0, 2, 1, 3).reshape(B, T, D))


def ssd_scan(x, log_a, Bm, Cm, chunk: int):
    """h_t = a_t·h_{t-1} + B_t x_tᵀ,  y_t = C_tᵀ h_t, per head, in chunks.

    x: (B, T, H, P) · log_a: (B, T, H), ≤ 0 · Bm, Cm: (B, T, N). All float32.
    Within a chunk the recurrence is a masked, decay-weighted attention (C Bᵀ ⊙ decay) x; across
    chunks a (B, H, N, P) state carries it. Memory per chunk is O(B·H·Q²), not O(B·T²·D).
    """
    Bsz, T, H, P = x.shape
    N = Bm.shape[-1]
    S = mx.zeros((Bsz, H, N, P), dtype=mx.float32)
    tri = mx.tril(mx.ones((chunk, chunk), dtype=mx.bool_))
    ys = []
    for s in range(0, T, chunk):
        e = min(s + chunk, T)
        q = e - s
        xc = x[:, s:e].transpose(0, 2, 1, 3)  # (B, H, q, P)
        L = mx.cumsum(log_a[:, s:e].transpose(0, 2, 1), axis=-1)  # (B, H, q)
        bc, cc = Bm[:, s:e], Cm[:, s:e]  # (B, q, N)
        diff = L[..., :, None] - L[..., None, :]  # (B, H, q, q): L_t − L_s
        decay = mx.exp(mx.where(tri[:q, :q], diff, -mx.inf))
        scores = (cc @ bc.transpose(0, 2, 1))[:, None]  # (B, 1, q, q)
        y = (scores * decay) @ xc
        y = y + mx.exp(L)[..., None] * (cc[:, None] @ S)
        w = mx.exp(L[..., -1:] - L)  # (B, H, q): decay from s to the chunk end
        S = mx.exp(L[..., -1])[..., None, None] * S + (bc[:, None].transpose(0, 1, 3, 2) * w[:, :, None, :]) @ xc
        ys.append(y.transpose(0, 2, 1, 3))
    return mx.concatenate(ys, axis=1)


class SSD(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        d, H, N = c.d_model, c.n_heads, c.ssm_state
        self.d, self.h, self.p, self.n, self.chunk = d, H, d // H, N, c.ssm_chunk
        self.in_proj = nn.Linear(d, 2 * d + 2 * N + H, bias=False)  # x, z, B, C, dt
        self.out_proj = nn.Linear(d, d, bias=False)
        self.norm = nn.RMSNorm(d, eps=c.eps)
        dt = mx.exp(mx.random.uniform(math.log(1e-3), math.log(1e-1), (H,)))
        self.dt_bias = dt + mx.log(-mx.expm1(-dt))  # softplus⁻¹(dt)
        self.A_log = mx.log(mx.random.uniform(1.0, 16.0, (H,)))
        self.D = mx.ones((H,))

    def __call__(self, u):
        B, T, _ = u.shape
        d, N, H, P = self.d, self.n, self.h, self.p
        x, z, Bm, Cm, dt = mx.split(self.in_proj(u), [d, 2 * d, 2 * d + N, 2 * d + 2 * N], axis=-1)
        x = nn.silu(x).astype(mx.float32).reshape(B, T, H, P)
        dt = nn.softplus(dt.astype(mx.float32) + self.dt_bias.astype(mx.float32))  # (B, T, H)
        log_a = -dt * mx.exp(self.A_log.astype(mx.float32))
        y = ssd_scan(x * dt[..., None], log_a, Bm.astype(mx.float32), Cm.astype(mx.float32), self.chunk)
        y = (y + x * self.D.astype(mx.float32)[:, None]).reshape(B, T, d)
        y = self.norm((y * nn.silu(z.astype(mx.float32))).astype(u.dtype))
        return self.out_proj(y)


class MLP(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.gate_up = nn.Linear(c.d_model, 2 * c.ffn_hidden, bias=False)
        self.down = nn.Linear(c.ffn_hidden, c.d_model, bias=False)

    def __call__(self, x):
        g, u = mx.split(self.gate_up(x), 2, axis=-1)
        return self.down(nn.silu(g) * u)


class Block(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.norm1 = nn.RMSNorm(c.d_model, eps=c.eps)
        self.mixer = Attention(c) if c.family == "llama" else SSD(c)
        self.norm2 = nn.RMSNorm(c.d_model, eps=c.eps)
        self.mlp = MLP(c)

    def __call__(self, x):
        x = x + self.mixer(self.norm1(x))
        return x + self.mlp(self.norm2(x))


class LM(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.config = c
        self.embed = nn.Embedding(c.vocab_size, c.d_model)
        self.layers = [Block(c) for _ in range(c.n_layers)]
        self.norm = nn.RMSNorm(c.d_model, eps=c.eps)

    def __call__(self, ids):
        h = self.embed(ids)
        for layer in self.layers:
            h = layer(h)
        return self.embed.as_linear(self.norm(h))


RESIDUAL_OUT = ("o_proj", "out_proj", "down")


def init_weights(model: LM):
    """GPT-2-style init: N(0, 0.02) for matrices and the embedding, with the projections that
    write into the residual stream scaled by 1/√(2L). Norm weights, dt_bias, A_log and D keep
    their constructor values. Call after `mx.random.seed(seed)`."""
    std = 0.02
    scaled = std / math.sqrt(2 * model.config.n_layers)
    new = []
    for name, p in tree_flatten(model.parameters()):
        leaf = name.split(".")[-2] if "." in name else name
        if p.ndim == 2:
            s = scaled if leaf in RESIDUAL_OUT else std
            p = mx.random.normal(p.shape) * s
        new.append((name, p))
    model.update(tree_unflatten(new))
    mx.eval(model.parameters())


def count_params(model: LM) -> dict:
    total = sum(p.size for _, p in tree_flatten(model.parameters()))
    emb = model.embed.weight.size
    return {"total": total, "embedding": emb, "non_embedding": total - emb}


def flops_per_token(c: ModelConfig, n_params: int) -> int:
    """Training FLOPs per token: 6N for the weights, plus attention's 6·L·T·d (forward and
    backward, causal half counted) for the transformer, or the SSD chunk terms for the SSM."""
    if c.family == "llama":
        mix = 6 * c.n_layers * c.ctx * c.d_model
    else:
        mix = 6 * c.n_layers * (c.ssm_chunk * (c.d_model + c.ssm_state) + 2 * c.ssm_state * c.d_model)
    return 6 * n_params + mix


def build(c: ModelConfig, seed: int) -> LM:
    mx.random.seed(seed)
    model = LM(c)
    init_weights(model)
    return model
