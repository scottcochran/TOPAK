//! The Persona bundle: `model.json`, `model.safetensors` and `tokenizer.json` in one directory.
//! A port of `slm/serve/serve.py:load_bundle`. Every check runs before the guest writes its first
//! line, so a bundle that does not match `model.json` never reaches a hello (ADR-0036 §2.1).

use std::path::Path;

use serde_json::Value;
use sha2::{Digest as _, Sha256};
use tokenizers::Tokenizer;

use crate::model::{Config, Model};

pub const EOT: &str = "<|endoftext|>";

pub struct Bundle {
    /// sha256 of `model.json`'s bytes: the Persona digest the launcher appraises (P5, P7).
    pub persona: String,
    pub desc: Value,
    pub model: Model,
    pub tok: Tokenizer,
    pub eot: Option<u32>,
}

pub fn sha256_hex(bytes: &[u8]) -> String {
    let d = Sha256::digest(bytes);
    d.iter().map(|b| format!("{b:02x}")).collect()
}

pub fn load(dir: &Path) -> Result<Bundle, String> {
    let read = |name: &str| std::fs::read(dir.join(name)).map_err(|e| format!("missing {}: {e}", dir.join(name).display()));
    let mj = read("model.json")?;
    let weights = read("model.safetensors")?;
    let tokj = read("tokenizer.json")?;
    let persona = sha256_hex(&mj);
    if let Ok(pinned) = std::env::var("SLM_MODEL_SHA256") {
        let pinned = pinned.trim().to_lowercase();
        if !pinned.is_empty() && pinned != persona {
            return Err(format!("model.json digest {} is not the pinned {}", &persona[..16], &pinned[..pinned.len().min(16)]));
        }
    }
    let desc: Value = serde_json::from_slice(&mj).map_err(|e| format!("model.json is not JSON: {e}"))?;
    for (field, name, bytes) in [("weights", "model.safetensors", &weights), ("tokenizer", "tokenizer.json", &tokj)] {
        let have = sha256_hex(bytes);
        let want = desc[field].as_str().unwrap_or("");
        if want != have {
            return Err(format!("{name} digest {} is not model.json's {field} {}", &have[..16], &want[..want.len().min(16)]));
        }
    }
    let cfg = Config::from_json(&desc["model_config"])?;
    let model = Model::load(cfg, &weights)?;
    let tok = Tokenizer::from_bytes(&tokj).map_err(|e| format!("tokenizer.json: {e}"))?;
    let vocab = tok.get_vocab_size(true);
    if vocab != model.cfg.vocab {
        return Err(format!("tokenizer vocab {vocab} is not the model's {}", model.cfg.vocab));
    }
    let eot = tok.token_to_id(EOT);
    Ok(Bundle { persona, desc, model, tok, eot })
}
