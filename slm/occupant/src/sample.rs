//! Generation, with `slm/serve/serve.py:generate`'s semantics: the window is the last `ctx` tokens,
//! greedy at temperature 0, otherwise temperature and top-k, stopping before the end-of-text
//! token. The sampler's random stream is this crate's own (xoshiro256** seeded by splitmix64), so
//! a seeded sample is deterministic here but does not match MLX's. Greedy output does.

use crate::model::Model;

pub struct Opts {
    pub max_new: usize,
    pub temperature: f32,
    pub top_k: usize,
    pub seed: u64,
}

struct Rng([u64; 4]);

impl Rng {
    fn new(seed: u64) -> Rng {
        let mut x = seed;
        let mut next = || {
            x = x.wrapping_add(0x9e3779b97f4a7c15);
            let mut z = x;
            z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
            z ^ (z >> 31)
        };
        Rng([next(), next(), next(), next()])
    }

    fn next_u64(&mut self) -> u64 {
        let s = &mut self.0;
        let r = s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = s[1] << 17;
        s[2] ^= s[0];
        s[3] ^= s[1];
        s[1] ^= s[2];
        s[0] ^= s[3];
        s[2] ^= t;
        s[3] = s[3].rotate_left(45);
        r
    }

    fn unit(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

pub fn argmax(xs: &[f32]) -> usize {
    let mut best = 0;
    for (i, &x) in xs.iter().enumerate() {
        if x > xs[best] {
            best = i;
        }
    }
    best
}

fn pick(logits: &[f32], o: &Opts, rng: &mut Rng) -> usize {
    if o.temperature <= 0.0 {
        return argmax(logits);
    }
    let mut l: Vec<f32> = logits.iter().map(|x| x / o.temperature).collect();
    if o.top_k > 0 && o.top_k < l.len() {
        let mut sorted = l.clone();
        sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let kth = sorted[sorted.len() - o.top_k];
        for x in &mut l {
            if *x < kth {
                *x = f32::NEG_INFINITY;
            }
        }
    }
    let max = l.iter().cloned().fold(f32::NEG_INFINITY, f32::max);
    let w: Vec<f64> = l.iter().map(|x| ((x - max) as f64).exp()).collect();
    let mut u = rng.unit() * w.iter().sum::<f64>();
    for (i, wi) in w.iter().enumerate() {
        if u < *wi {
            return i;
        }
        u -= wi;
    }
    argmax(&l)
}

pub fn generate(m: &Model, ids: &[u32], o: &Opts, eot: Option<u32>) -> Vec<u32> {
    let ctx = m.cfg.ctx;
    let mut rng = Rng::new(o.seed);
    let mut out: Vec<u32> = ids.to_vec();
    let mut cache = m.cache();
    for _ in 0..o.max_new {
        // While the window has not slid, the cache is exact; once it slides, positions restart at 0
        // for the new window, so it is recomputed (serve.py recomputes every step).
        let logits = if out.len() <= ctx {
            let fresh = out[cache.len..].to_vec();
            m.forward(&mut cache, &fresh)
        } else {
            let mut c = m.cache();
            m.forward(&mut c, &out[out.len() - ctx..])
        };
        let next = pick(&logits, o, &mut rng) as u32;
        if Some(next) == eot {
            break;
        }
        out.push(next);
    }
    out.split_off(ids.len())
}
