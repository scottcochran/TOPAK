//! Signed statements: the stand-in for ADR-0025's opaque `Authentic`.
//!
//! PROVISIONAL (Authentic): ADR-0025 leaves `Authentic` opaque and custody a declaration. This
//! baseline instantiates it as Ed25519 over the canonical JSON of the statement body, with a
//! domain-separation tag so a signature for one purpose cannot be replayed as another.

use ed25519_dalek::{Signature, Signer as _, SigningKey, Verifier, VerifyingKey};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeSet;

use crate::types::canonical_json;

/// Hex-encoded Ed25519 public key.
pub type KeyHex = String;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Signed {
    pub key: KeyHex,
    pub sig: String,
}

/// Bytes a key signs for `purpose` over `body`.
pub fn signing_bytes(purpose: &str, body: &Value) -> Vec<u8> {
    let mut out = format!("topak/{purpose}/v1\n").into_bytes();
    out.extend(canonical_json(body));
    out
}

/// Sign `body` for `purpose` with a 32-byte Ed25519 secret. The `topak sign` helper is this.
pub fn sign(purpose: &str, body: &Value, secret: &[u8; 32]) -> Signed {
    let sk = SigningKey::from_bytes(secret);
    let sig = sk.sign(&signing_bytes(purpose, body));
    Signed { key: hex::encode(sk.verifying_key().to_bytes()), sig: hex::encode(sig.to_bytes()) }
}

pub fn verify(purpose: &str, body: &Value, s: &Signed) -> bool {
    let Ok(kb) = hex::decode(&s.key) else { return false };
    let Ok(kb): Result<[u8; 32], _> = kb.try_into() else { return false };
    let Ok(key) = VerifyingKey::from_bytes(&kb) else { return false };
    let Ok(sb) = hex::decode(&s.sig) else { return false };
    let Ok(sb): Result<[u8; 64], _> = sb.try_into() else { return false };
    key.verify(&signing_bytes(purpose, body), &Signature::from_bytes(&sb)).is_ok()
}

/// The set of distinct keys in `sigs` that validly signed `body` for `purpose` and belong to
/// `allowed`. Duplicate or foreign signatures count for nothing.
pub fn valid_signers(purpose: &str, body: &Value, sigs: &[Signed], allowed: &BTreeSet<KeyHex>) -> BTreeSet<KeyHex> {
    sigs.iter().filter(|s| allowed.contains(&s.key) && verify(purpose, body, s)).map(|s| s.key.clone()).collect()
}
