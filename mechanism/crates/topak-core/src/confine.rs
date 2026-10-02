//! Confinement: the profile, the nonce, the appraisal and the session proof (ADR-0034, ADR-0036).
//!
//! Everything here is checked at apply, so it is deterministic and reads no clock and no file
//! (ADR-0033 §4). The launcher that produces these values is `topak-contain`; what a replica
//! believes is only what this module and `State` check.
//!
//! The profile is the constant and the rung is the variable (ADR-0036 §1 R1): one schema at every
//! rung, appraised differently. Rung 1 is the mechanism's own assertion, rung 3 a verifier's
//! signed statement under a key in the issued rules (ADR-0025 §1 (f)). Rung 2 is a seam.

use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

use crate::authentic::{KeyHex, Signed};
use crate::types::*;

/// The seven clauses of a Build profile (ADR-0034 §1).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub enum Clause {
    P1,
    P2,
    P3,
    P4,
    P5,
    P6,
    P7,
}

impl Clause {
    pub const ALL: [Clause; 7] = [Clause::P1, Clause::P2, Clause::P3, Clause::P4, Clause::P5, Clause::P6, Clause::P7];
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ClauseVerdict {
    Pass,
    Fail,
    Vacuous,
}

impl ClauseVerdict {
    pub fn as_str(self) -> &'static str {
        match self {
            ClauseVerdict::Pass => "pass",
            ClauseVerdict::Fail => "fail",
            ClauseVerdict::Vacuous => "vacuous",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ClauseDecl {
    pub verdict: ClauseVerdict,
    pub why: String,
}

/// The Persona bundle's reference value: the digest of `model.json`, which pins weights and
/// tokenizer (ADR-0036 §1). The name is the one `slm/serve/profile-host-rung0.json` uses.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersonaRef {
    #[serde(default)]
    pub model_json_sha256: Option<Digest>,
}

/// P7's two reference values (ADR-0034 §1). Changing either is a new profile and a new promotion.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ReferenceValues {
    /// The expected launch measurement, as the platform reports it. Rungs 2 and 3.
    #[serde(default)]
    pub launch_measurement: Option<String>,
    /// The minimum platform TCB version. Rung 3.
    #[serde(default)]
    pub min_tcb: Option<u64>,
}

fn build() -> Domain {
    Domain::Build
}

/// A confinement profile (ADR-0036 §1). Its digest is the digest of the file's bytes, and that
/// digest is the first element of the lease's `confinement` field (ADR-0031 §1). Fields beginning
/// with `_` in the file are commentary and ignored.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Profile {
    /// The guest image by content digest. `None` for a host process (rung 0 only).
    #[serde(default)]
    pub image: Option<Digest>,
    /// The runtime constraints the launcher applies. Opaque here; typed by the backend.
    #[serde(default)]
    pub launch: Value,
    #[serde(default)]
    pub channel: Value,
    #[serde(default)]
    pub persona: PersonaRef,
    #[serde(default)]
    pub reference: ReferenceValues,
    pub clauses: BTreeMap<Clause, ClauseDecl>,
    #[serde(default)]
    pub subtractions: BTreeMap<Clause, String>,
    /// Build and Run share the schema, not the profile (ADR-0034 §1).
    #[serde(default = "build")]
    pub domain: Domain,
}

impl Profile {
    pub fn parse(text: &str) -> Result<Profile, String> {
        serde_json::from_str(text).map_err(|e| format!("profile does not parse: {e}"))
    }

    pub fn verdict(&self, c: Clause) -> Option<ClauseVerdict> {
        self.clauses.get(&c).map(|d| d.verdict)
    }

    /// ADR-0036 §1: a profile that omits a clause is malformed, and every `fail` names what would
    /// have to be removed for it to pass. Rung-independent: the profile is the constant.
    pub fn check_well_formed(&self) -> Vec<String> {
        let mut out = Vec::new();
        for c in Clause::ALL {
            match self.clauses.get(&c) {
                None => out.push(format!("{c:?} is missing")),
                Some(d) if d.verdict == ClauseVerdict::Fail && !self.subtractions.contains_key(&c) => {
                    out.push(format!("{c:?} fails and names no subtraction"))
                }
                _ => {}
            }
        }
        out
    }

    /// The reference values a rung appraises against (P7). Rung 1 compares the image and the
    /// Persona (ADR-0036 §2.2); rungs 2 and 3 add the launch measurement; rung 3 the TCB floor.
    pub fn check_for_rung(&self, rung: u8) -> Result<(), String> {
        if rung == 0 {
            return Ok(());
        }
        let need = |ok: bool, what: &str| if ok { Ok(()) } else { Err(format!("rung {rung} needs P7's {what}")) };
        need(self.image.is_some(), "image digest")?;
        need(self.persona.model_json_sha256.is_some(), "Persona digest")?;
        if rung >= 2 {
            need(self.reference.launch_measurement.is_some(), "launch measurement")?;
        }
        if rung >= 3 {
            need(self.reference.min_tcb.is_some(), "minimum TCB version")?;
        }
        Ok(())
    }

    /// ADR-0034 §4's profile conjunct: P3 to P5 hold. P4 is the domain's: for Build, tools are
    /// Wasm components; for Run, channel fidelity (ADR-0034 A2, pending). `vacuous` holds only for
    /// an alphabet without the variant that reaches a tool, `Invoke` or `Actuate` (D-0034-3,
    /// D-0034-6). Returns what fails; empty means the conjunct holds.
    pub fn meets_p3_p5(&self, alphabet: &BTreeSet<ActionKind>) -> Vec<String> {
        let tool = match self.domain {
            Domain::Build => ActionKind::Invoke,
            Domain::Run => ActionKind::Actuate,
        };
        let mut out = Vec::new();
        if self.verdict(Clause::P3) != Some(ClauseVerdict::Pass) {
            out.push("P3 does not pass: a launcher is reachable from the principal".into());
        }
        match self.verdict(Clause::P4) {
            Some(ClauseVerdict::Pass) => {}
            Some(ClauseVerdict::Vacuous) if !alphabet.contains(&tool) => {}
            Some(ClauseVerdict::Vacuous) => out.push(format!("P4 is vacuous but the alphabet holds {tool}")),
            _ if self.domain == Domain::Run => {
                out.push("P4 does not pass: a Run tool is not held to its declared channel".into())
            }
            _ => out.push("P4 does not pass: a tool is not a Wasm component".into()),
        }
        if self.verdict(Clause::P5) != Some(ClauseVerdict::Pass) {
            out.push("P5 does not pass: inference is not inside the measured guest".into());
        }
        out
    }
}

/// A workspace digest: SHA-256 over the files sorted by path, each as `path \0 bytes \0`. The
/// node's `workspace_digest` is this over the round's workspace; promotion keys on it.
pub fn workspace_digest(files: impl IntoIterator<Item = (String, Vec<u8>)>) -> Digest {
    let mut files: Vec<(String, Vec<u8>)> = files.into_iter().collect();
    files.sort();
    let mut bytes = Vec::new();
    for (rel, content) in files {
        bytes.extend(rel.as_bytes());
        bytes.push(0);
        bytes.extend(content);
        bytes.push(0);
    }
    Digest::of(&bytes)
}

/// The workspace a profile is promoted as. PROVISIONAL (profile-artifact): one file,
/// `profile.json`, so that the promoted artifact names exactly the bytes whose digest the lease
/// carries.
pub const PROFILE_FILE: &str = "profile.json";

pub fn profile_artifact(bytes: &[u8]) -> Digest {
    workspace_digest([(PROFILE_FILE.to_string(), bytes.to_vec())])
}

/// The nonce's preimage (ADR-0034 §3.1): from the log, never a clock.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct NonceInput {
    pub epoch: Epoch,
    /// The committed log index at the request.
    pub index: LogIndex,
    pub principal: String,
    pub round: Round,
}

impl NonceInput {
    pub fn digest(&self) -> Digest {
        Digest::of_json(self)
    }
}

/// What the evidence must bind: the nonce and the guest's session public key (ADR-0034 §3.1).
pub fn report_data(nonce: &Digest, session_key: Option<&KeyHex>) -> Digest {
    Digest::of_json(&json!({ "nonce": nonce, "sessionKey": session_key }))
}

/// The three verdicts (ADR-0034 §3.3). Not `Verdict`, which is a vote's.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Appraised {
    Attested,
    Unattestable,
    Contested,
}

impl Appraised {
    pub fn as_str(self) -> &'static str {
        match self {
            Appraised::Attested => "attested",
            Appraised::Unattestable => "unattestable",
            Appraised::Contested => "contested",
        }
    }
}

/// The platform a statement is about. `sim-snp` is the simulator's, and every surface that shows
/// a lease resting on it says SIMULATED.
pub const PLATFORM_LAUNCHER: &str = "launcher";
pub const PLATFORM_SIM_SNP: &str = "sim-snp";

/// What an appraiser asserts, and at rung 3 what the verifier signs (purpose `appraisal`).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppraisalStatement {
    pub nonce: NonceInput,
    pub profile: Digest,
    pub persona: Digest,
    pub rung: u8,
    pub verdict: Appraised,
    /// The digest of the evidence bytes. The bytes are retained by the appraising node.
    pub evidence: Digest,
    pub session_key: Option<KeyHex>,
    pub measurement: Option<String>,
    pub tcb: Option<u64>,
    pub platform: String,
}

pub const APPRAISAL_PURPOSE: &str = "appraisal";

/// An appraisal as it enters the log. `instance` is the launched guest the appraising replica
/// started: the `gen` of `Confinement.tla`. It is the launcher's to name, outside the signature;
/// at rungs 2 and 3 the signed session key is what binds the guest.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Appraisal {
    pub statement: AppraisalStatement,
    pub instance: Digest,
    #[serde(default)]
    pub signature: Option<Signed>,
}

impl Appraisal {
    pub fn body(&self) -> Value {
        serde_json::to_value(&self.statement).expect("serializable")
    }
}

/// What a grant leaves on the lease record: replicated, so every replica can check a session
/// proof against it. Not a lease field: ADR-0031 §1's set is closed.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Attestation {
    pub verdict: Appraised,
    /// The nonce's epoch: `nEpoch` of `Confinement.tla`.
    pub n_epoch: Epoch,
    pub nonce_index: LogIndex,
    pub instance: Digest,
    pub session_key: Option<KeyHex>,
    pub evidence: Digest,
    /// The issued verifier key that signed, at rung 3.
    pub verified_by: Option<KeyHex>,
    pub platform: String,
}

/// One action's proof that the attested guest sent it (ADR-0034 §3.5): at rungs 2 and 3 it
/// replaces the bearer token. `op` is the digest of the action the guest signed.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SessionProof {
    pub ctr: u64,
    pub op: Digest,
    pub sig: String,
}

pub const AGENT_OP_PURPOSE: &str = "agent-op";

pub fn session_body(fence: LogIndex, epoch: Epoch, ctr: u64, op: &Digest) -> Value {
    json!({ "fence": fence, "epoch": epoch, "ctr": ctr, "op": op })
}

/// ADR-0017's provenance axis, issued per Persona digest. The archetype and rung 1 are in house.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Provenance {
    InHousePretrain,
    InHouseFinetune,
    AttestedExternal,
    AssertedExternal,
}

impl Provenance {
    pub fn in_house(self) -> bool {
        matches!(self, Provenance::InHousePretrain | Provenance::InHouseFinetune)
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Provenance::InHousePretrain => "in_house_pretrain",
            Provenance::InHouseFinetune => "in_house_finetune",
            Provenance::AttestedExternal => "attested_external",
            Provenance::AssertedExternal => "asserted_external",
        }
    }
}

/// ADR-0035's criterion, in force when an anchor issuance carries it. `Contained` reads only
/// whether it is set (ADR-0034 §4); what it names is the record and the values it was ratified
/// with.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Criterion {
    pub record: String,
    pub independence_table: Digest,
    pub floor_values: Digest,
}

/// `Contained(p)` as a lookup: `contained` with every failing conjunct named, so a `Mediated`
/// verdict says why. `simulated` marks a lease whose attestation came from the simulator.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Containment {
    pub contained: bool,
    pub because: Vec<String>,
    pub simulated: bool,
}
