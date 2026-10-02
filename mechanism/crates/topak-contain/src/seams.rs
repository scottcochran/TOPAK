//! Seams: the backends this design names and does not build. Each launches nothing and says why,
//! so a configuration that names one fails at the first launch, not silently.
//!
//! - Rung 2 (ADR-0034 §2): a guest that boots, Firecracker or Kata, with a measured-boot TPM quote
//!   appraised by the mechanism against P7. `State::apply_grant` refuses rung 2 until it exists.
//! - Rung 3 on hardware: an SEV-SNP or TDX confidential VM whose report covers firmware, kernel,
//!   initrd, root hash and the Persona digest, appraised by an independent verifier
//!   (`appraise::HttpVerifier`). Accelerator attestation (P5, T-0045-21) is a further field of the
//!   evidence, reserved and undefined.

use anyhow::bail;

use crate::BoxFuture;
use crate::backend::{Backend, LaunchRequest, LaunchedGuest};

macro_rules! seam {
    ($name:ident, $rung:expr, $kind:expr, $why:expr) => {
        pub struct $name;
        impl Backend for $name {
            fn rung(&self) -> u8 {
                $rung
            }
            fn kind(&self) -> &'static str {
                $kind
            }
            fn launch<'a>(&'a self, _req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>> {
                Box::pin(async { bail!($why) })
            }
        }
    };
}

seam!(MeasuredBootBackend, 2, "measured-boot", "rung 2 (Firecracker or Kata with a TPM quote) is not built");
seam!(SnpBackend, 3, "snp", "an SEV-SNP backend is not built: it needs the hardware");
seam!(TdxBackend, 3, "tdx", "a TDX backend is not built: it needs the hardware");
