//! The `llama` family of `slm/model.py`, forward pass only, in f32: pre-norm decoder, RMSNorm,
//! RoPE (`traditional=False`), SwiGLU, no biases, tied input/output embeddings. Parameter names
//! and layouts are the checkpoint's: `embed.weight`, `layers.N.{norm1,norm2}.weight`,
//! `layers.N.mixer.{qkv,o_proj}.weight`, `layers.N.mlp.{gate_up,down}.weight`, `norm.weight`.
//! An `mlx.nn.Linear` weight is (out, in) and computes `x @ W.T`.

use safetensors::{Dtype, SafeTensors};
use serde_json::Value;

#[derive(Clone, Debug)]
pub struct Config {
    pub vocab: usize,
    pub d: usize,
    pub layers: usize,
    pub heads: usize,
    pub ctx: usize,
    pub ffn: usize,
    pub rope_base: f32,
    pub eps: f32,
}

impl Config {
    pub fn from_json(v: &Value) -> Result<Config, String> {
        let u = |k: &str| v[k].as_u64().map(|x| x as usize).ok_or_else(|| format!("model_config.{k} missing"));
        if v["family"].as_str() != Some("llama") {
            return Err(format!("family {} is not llama; this occupant runs the decoder-transformer only", v["family"]));
        }
        let c = Config {
            vocab: u("vocab_size")?,
            d: u("d_model")?,
            layers: u("n_layers")?,
            heads: u("n_heads")?,
            ctx: u("ctx")?,
            ffn: u("ffn_hidden")?,
            rope_base: u("rope_base")? as f32,
            eps: u("norm_eps_e6")? as f32 * 1e-6,
        };
        if c.d % c.heads != 0 || c.ffn == 0 {
            return Err("d_model must divide by n_heads and ffn_hidden must be set".into());
        }
        Ok(c)
    }
}

struct Layer {
    norm1: Vec<f32>,
    qkv: Vec<f32>,
    o: Vec<f32>,
    norm2: Vec<f32>,
    gate_up: Vec<f32>,
    down: Vec<f32>,
}

pub struct Model {
    pub cfg: Config,
    embed: Vec<f32>,
    layers: Vec<Layer>,
    norm: Vec<f32>,
    inv_freq: Vec<f32>,
}

/// Keys and values per layer, one row of `d` per position, for positions `0..len`.
pub struct Cache {
    k: Vec<Vec<f32>>,
    v: Vec<Vec<f32>>,
    pub len: usize,
}

fn tensor(st: &SafeTensors, name: &str, shape: &[usize]) -> Result<Vec<f32>, String> {
    let t = st.tensor(name).map_err(|e| format!("{name}: {e}"))?;
    if t.dtype() != Dtype::F32 {
        return Err(format!("{name} is {:?}, not F32", t.dtype()));
    }
    if t.shape() != shape {
        return Err(format!("{name} has shape {:?}, expected {shape:?}", t.shape()));
    }
    Ok(t.data().chunks_exact(4).map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]])).collect())
}

/// y[m×n] = x[m×k] · W[n×k]ᵀ
fn linear(x: &[f32], m: usize, k: usize, w: &[f32], n: usize) -> Vec<f32> {
    let mut y = vec![0f32; m * n];
    unsafe {
        matrixmultiply::sgemm(
            m, k, n, 1.0,
            x.as_ptr(), k as isize, 1,
            w.as_ptr(), 1, k as isize,
            0.0, y.as_mut_ptr(), n as isize, 1,
        );
    }
    y
}

fn rms_norm(x: &[f32], w: &[f32], eps: f32) -> Vec<f32> {
    let d = w.len();
    let mut y = vec![0f32; x.len()];
    for (row, out) in x.chunks_exact(d).zip(y.chunks_exact_mut(d)) {
        let ms = row.iter().map(|v| v * v).sum::<f32>() / d as f32;
        let r = 1.0 / (ms + eps).sqrt();
        for i in 0..d {
            out[i] = row[i] * r * w[i];
        }
    }
    y
}

impl Model {
    pub fn load(cfg: Config, bytes: &[u8]) -> Result<Model, String> {
        let st = SafeTensors::deserialize(bytes).map_err(|e| format!("model.safetensors: {e}"))?;
        let (d, f) = (cfg.d, cfg.ffn);
        let expected = 2 + cfg.layers * 6;
        if st.len() != expected {
            return Err(format!("model.safetensors has {} tensors, expected {expected}", st.len()));
        }
        let mut layers = Vec::with_capacity(cfg.layers);
        for i in 0..cfg.layers {
            let p = |s: &str| format!("layers.{i}.{s}");
            layers.push(Layer {
                norm1: tensor(&st, &p("norm1.weight"), &[d])?,
                qkv: tensor(&st, &p("mixer.qkv.weight"), &[3 * d, d])?,
                o: tensor(&st, &p("mixer.o_proj.weight"), &[d, d])?,
                norm2: tensor(&st, &p("norm2.weight"), &[d])?,
                gate_up: tensor(&st, &p("mlp.gate_up.weight"), &[2 * f, d])?,
                down: tensor(&st, &p("mlp.down.weight"), &[d, f])?,
            });
        }
        let hd = d / cfg.heads;
        let inv_freq = (0..hd / 2).map(|i| cfg.rope_base.powf(-((2 * i) as f32) / hd as f32)).collect();
        Ok(Model {
            embed: tensor(&st, "embed.weight", &[cfg.vocab, d])?,
            norm: tensor(&st, "norm.weight", &[d])?,
            layers,
            inv_freq,
            cfg,
        })
    }

    pub fn cache(&self) -> Cache {
        Cache { k: vec![Vec::new(); self.cfg.layers], v: vec![Vec::new(); self.cfg.layers], len: 0 }
    }

    /// RoPE, `traditional=False`: the head's first and second halves are the pair rotated.
    fn rope(&self, x: &mut [f32], pos: usize) {
        let hd = self.cfg.d / self.cfg.heads;
        let half = hd / 2;
        for head in x.chunks_exact_mut(hd) {
            for i in 0..half {
                let (s, c) = (pos as f32 * self.inv_freq[i]).sin_cos();
                let (a, b) = (head[i], head[i + half]);
                head[i] = a * c - b * s;
                head[i + half] = a * s + b * c;
            }
        }
    }

    /// Run `ids` at positions `cache.len ..`, append their keys and values, and return the logits
    /// of the last position.
    pub fn forward(&self, cache: &mut Cache, ids: &[u32]) -> Vec<f32> {
        let c = &self.cfg;
        let (d, t, p0) = (c.d, ids.len(), cache.len);
        let hd = d / c.heads;
        let scale = (hd as f32).powf(-0.5);
        let mut h = vec![0f32; t * d];
        for (row, &id) in h.chunks_exact_mut(d).zip(ids) {
            row.copy_from_slice(&self.embed[id as usize * d..(id as usize + 1) * d]);
        }
        for (li, l) in self.layers.iter().enumerate() {
            // Attention
            let x = rms_norm(&h, &l.norm1, c.eps);
            let qkv = linear(&x, t, d, &l.qkv, 3 * d);
            let mut q = vec![0f32; t * d];
            for j in 0..t {
                let r = &qkv[j * 3 * d..(j + 1) * 3 * d];
                q[j * d..(j + 1) * d].copy_from_slice(&r[..d]);
                let mut k = r[d..2 * d].to_vec();
                self.rope(&mut q[j * d..(j + 1) * d], p0 + j);
                self.rope(&mut k, p0 + j);
                cache.k[li].extend_from_slice(&k);
                cache.v[li].extend_from_slice(&r[2 * d..]);
            }
            let (ks, vs) = (&cache.k[li], &cache.v[li]);
            let mut o = vec![0f32; t * d];
            let mut scores = vec![0f32; p0 + t];
            for j in 0..t {
                let n = p0 + j + 1; // causal: positions 0 ..= p0 + j
                for hh in 0..c.heads {
                    let qh = &q[j * d + hh * hd..j * d + (hh + 1) * hd];
                    let mut max = f32::NEG_INFINITY;
                    for s in 0..n {
                        let kh = &ks[s * d + hh * hd..s * d + (hh + 1) * hd];
                        let v = qh.iter().zip(kh).map(|(a, b)| a * b).sum::<f32>() * scale;
                        scores[s] = v;
                        max = max.max(v);
                    }
                    let mut z = 0f32;
                    for sc in &mut scores[..n] {
                        *sc = (*sc - max).exp();
                        z += *sc;
                    }
                    let oh = &mut o[j * d + hh * hd..j * d + (hh + 1) * hd];
                    for s in 0..n {
                        let w = scores[s] / z;
                        let vh = &vs[s * d + hh * hd..s * d + (hh + 1) * hd];
                        for (a, b) in oh.iter_mut().zip(vh) {
                            *a += w * b;
                        }
                    }
                }
            }
            let a = linear(&o, t, d, &l.o, d);
            for (x, y) in h.iter_mut().zip(&a) {
                *x += y;
            }
            // SwiGLU: gate_up splits into gate (first half) and up (second half).
            let x = rms_norm(&h, &l.norm2, c.eps);
            let gu = linear(&x, t, d, &l.gate_up, 2 * c.ffn);
            let mut act = vec![0f32; t * c.ffn];
            for j in 0..t {
                let r = &gu[j * 2 * c.ffn..(j + 1) * 2 * c.ffn];
                for i in 0..c.ffn {
                    let g = r[i];
                    act[j * c.ffn + i] = g / (1.0 + (-g).exp()) * r[c.ffn + i];
                }
            }
            let m = linear(&act, t, c.ffn, &l.down, d);
            for (x, y) in h.iter_mut().zip(&m) {
                *x += y;
            }
        }
        cache.len += t;
        let last = rms_norm(&h[(t - 1) * d..], &self.norm, c.eps);
        linear(&last, 1, d, &self.embed, c.vocab)
    }
}
