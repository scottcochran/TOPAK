//! A simulated rung 3. SIMULATED: test doubles for the CPU vendor's root (T-0045-16) and the
//! independent verifier (T-0045-17), both played by keys a test generates.
//!
//! `SimPlatform` stands in for the security processor: it measures the launch, and signs a report
//! binding what the guest asks it to. `SimVerifier` stands in for the verifier: it checks the
//! report against the platform's endorsement key and the profile's reference values, and signs a
//! verdict. Every rung-3 path in the mechanism runs against them: the nonce, the bound session
//! key, the signed verdict, Contested, the fence. None of it is confinement, and every surface
//! that shows a lease resting on them says SIMULATED.
//!
//! What the measurement covers: the guest binary, its arguments and the Persona bundle's
//! `model.json`. ADR-0034 §2 has it cover the profile digest too, while P7 has the profile carry
//! the expected measurement; a measurement cannot cover the file that names it. The simulator
//! measures the parts and leaves the profile digest out, and the design record reports it.

use std::path::PathBuf;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

use serde_json::json;
use tokio::sync::Semaphore;
use topak_core::Digest;
use topak_core::authentic::{self, KeyHex, Signed};
use topak_core::confine::*;

use crate::BoxFuture;
use crate::SimReport;
use crate::appraise::*;
use crate::backend::*;
use crate::guest::{GuestEvidence, GuestHello};

pub const REPORT_PURPOSE: &str = "sim-report";

/// The launch measurement the simulated platform computes.
pub fn measurement(binary: &Digest, args: &[String], persona: &Digest) -> String {
    Digest::of_json(&json!({ "binary": binary, "args": args, "persona": persona })).0
}

pub struct SimPlatform {
    chip: [u8; 32],
    pub tcb: AtomicU64,
}

impl SimPlatform {
    pub fn new(chip: [u8; 32], tcb: u64) -> Arc<Self> {
        Arc::new(SimPlatform { chip, tcb: AtomicU64::new(tcb) })
    }

    /// The endorsement key a verifier trusts for this platform.
    pub fn endorsement_key(&self) -> KeyHex {
        authentic::sign("key", &serde_json::Value::Null, &self.chip).key
    }

    fn report(&self, measurement: &str, report_data: &Digest) -> (SimReport, Signed) {
        let report = SimReport {
            measurement: measurement.into(),
            report_data: report_data.clone(),
            tcb: self.tcb.load(Ordering::SeqCst),
            platform: PLATFORM_SIM_SNP.into(),
        };
        let body = serde_json::to_value(&report).expect("serializable");
        let sig = authentic::sign(REPORT_PURPOSE, &body, &self.chip);
        (report, sig)
    }
}

/// A process launch measured by a `SimPlatform`. `rogue` launches with an argument the profile
/// did not measure: a different image, as the host power of ADR-0034 §5 row 3. `tamper` kills
/// every running guest, which is what the hardware is assumed to do to an altered one (row 4).
pub struct SimCvmBackend {
    pub command: PathBuf,
    pub args: Vec<String>,
    pub model: PathBuf,
    pub platform: Arc<SimPlatform>,
    pub rogue: AtomicBool,
    live: Mutex<Vec<Arc<ChildSlot>>>,
}

impl SimCvmBackend {
    pub fn new(command: PathBuf, args: Vec<String>, model: PathBuf, platform: Arc<SimPlatform>) -> Self {
        SimCvmBackend { command, args, model, platform, rogue: AtomicBool::new(false), live: Mutex::new(Vec::new()) }
    }

    /// The measurement an honest launch of this backend produces: what a profile names.
    pub fn expected_measurement(&self) -> anyhow::Result<String> {
        Ok(measurement(&file_digest(&self.command)?, &self.args, &file_digest(&self.model)?))
    }

    pub fn tamper(&self) {
        for c in self.live.lock().unwrap().drain(..) {
            c.kill();
        }
    }
}

pub struct SimGuest {
    instance: Digest,
    measurement: String,
    platform: Arc<SimPlatform>,
    child: Arc<ChildSlot>,
}

impl Backend for SimCvmBackend {
    fn rung(&self) -> u8 {
        3
    }

    fn kind(&self) -> &'static str {
        "sim-cvm"
    }

    fn launch<'a>(&'a self, _req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>> {
        Box::pin(async move {
            let mut args = self.args.clone();
            if self.rogue.load(Ordering::SeqCst) {
                args.push("--rogue".into());
            }
            let measured = measurement(&file_digest(&self.command)?, &args, &file_digest(&self.model)?);
            let instance = new_instance();
            let (child, io) = spawn(&self.command, &args, &instance, true)?;
            let child = ChildSlot::new(child);
            self.live.lock().unwrap().push(child.clone());
            let handle = Arc::new(SimGuest { instance, measurement: measured, platform: self.platform.clone(), child });
            Ok(LaunchedGuest { handle, io })
        })
    }
}

impl GuestHandle for SimGuest {
    fn instance(&self) -> &Digest {
        &self.instance
    }

    fn evidence(&self, from_guest: &GuestEvidence, _hello: &GuestHello) -> anyhow::Result<Evidence> {
        let (report, signature) = self.platform.report(&self.measurement, &from_guest.report_data);
        Ok(Evidence::SimSnp { report, signature })
    }

    fn destroy(&self) -> BoxFuture<'_, ()> {
        self.child.kill();
        Box::pin(async {})
    }
}

/// The simulated independent verifier. Its knobs are the test's: `reachable` (F14), a TCB floor
/// above the profile's (a vendor withdrawal it learned of, F17), and a gate that holds an
/// appraisal so a test can fence the epoch while it is pending (`M_STALE`).
pub struct SimVerifier {
    secret: [u8; 32],
    endorsement: KeyHex,
    pub reachable: AtomicBool,
    pub min_tcb: AtomicU64,
    pub gate: Mutex<Option<Arc<Semaphore>>>,
}

impl SimVerifier {
    pub fn new(secret: [u8; 32], endorsement: KeyHex) -> Self {
        SimVerifier {
            secret,
            endorsement,
            reachable: AtomicBool::new(true),
            min_tcb: AtomicU64::new(0),
            gate: Mutex::new(None),
        }
    }

    /// The key an anchor issuance must put in `verifier_keys` for this verifier to count.
    pub fn key(&self) -> KeyHex {
        authentic::sign("key", &serde_json::Value::Null, &self.secret).key
    }
}

impl Appraiser for SimVerifier {
    fn rung(&self) -> u8 {
        3
    }

    fn appraise<'a>(
        &'a self,
        ctx: AppraiseCtx<'a>,
        ev: &'a Evidence,
    ) -> BoxFuture<'a, Result<Statement, VerifierError>> {
        Box::pin(async move {
            let gate = self.gate.lock().unwrap().clone();
            if let Some(g) = gate {
                g.acquire().await.map_err(|_| VerifierError::Unreachable)?.forget();
            }
            if !self.reachable.load(Ordering::SeqCst) {
                return Err(VerifierError::Unreachable);
            }
            let Evidence::SimSnp { report, signature } = ev else {
                return Err(VerifierError::Malformed("not a simulated report".into()));
            };
            let body = serde_json::to_value(report).expect("serializable");
            if signature.key != self.endorsement || !authentic::verify(REPORT_PURPOSE, &body, signature) {
                return Err(VerifierError::Malformed("the report is not the platform's".into()));
            }
            if report.report_data != report_data(&ctx.nonce.digest(), ctx.hello.session_key.as_ref()) {
                return Err(VerifierError::Unbound);
            }
            let floor = ctx.profile.reference.min_tcb.unwrap_or(0).max(self.min_tcb.load(Ordering::SeqCst));
            if report.tcb < floor {
                return Err(VerifierError::EndorsementExpired(format!("TCB {} is below {floor}", report.tcb)));
            }
            let Some(persona) = ctx.profile.persona.model_json_sha256.clone() else {
                return Err(VerifierError::Malformed("the profile names no Persona".into()));
            };
            let verdict = if ctx.profile.reference.launch_measurement.as_deref() == Some(report.measurement.as_str()) {
                Appraised::Attested
            } else {
                Appraised::Contested
            };
            let statement = AppraisalStatement {
                nonce: ctx.nonce.clone(),
                profile: ctx.profile_digest.clone(),
                persona,
                rung: 3,
                verdict,
                evidence: ev.digest(),
                session_key: ctx.hello.session_key.clone(),
                measurement: Some(report.measurement.clone()),
                tcb: Some(report.tcb),
                platform: PLATFORM_SIM_SNP.into(),
            };
            let sig = authentic::sign(APPRAISAL_PURPOSE, &serde_json::to_value(&statement).unwrap(), &self.secret);
            Ok((statement, Some(sig)))
        })
    }
}
