//! Appraisal: what the evidence is worth (ADR-0034 §3.3).
//!
//! An appraiser returns a statement or Unattestable. Unattestable is never ordered: a refusal
//! needs no quorum and grants nothing, at no rung (ADR-0034 §3.3, PC/EC). Contested is a
//! statement, because it is ordered: it revokes the principal.

use topak_core::Digest;
use topak_core::authentic::Signed;
use topak_core::confine::*;

use crate::BoxFuture;
use crate::backend::Evidence;
use crate::guest::GuestHello;

pub struct AppraiseCtx<'a> {
    pub nonce: &'a NonceInput,
    pub profile: &'a Profile,
    pub profile_digest: &'a Digest,
    pub hello: &'a GuestHello,
}

/// A statement and, at rung 3, the verifier's signature over it.
pub type Statement = (AppraisalStatement, Option<Signed>);

/// Why no statement: every cause is Unattestable (ADR-0034 §3.3).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum VerifierError {
    /// The verifier did not answer. PC/EC: no grant; live leases run to renewal (F14).
    Unreachable,
    /// The platform's TCB is below what the profile or the verifier accepts.
    EndorsementExpired(String),
    /// The report does not bind this nonce and this session key: stale, or another guest's.
    Unbound,
    Malformed(String),
}

impl std::fmt::Display for VerifierError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            VerifierError::Unreachable => write!(f, "the verifier is unreachable"),
            VerifierError::EndorsementExpired(s) => write!(f, "endorsement expired: {s}"),
            VerifierError::Unbound => write!(f, "the report does not bind this nonce and session key"),
            VerifierError::Malformed(s) => write!(f, "malformed evidence: {s}"),
        }
    }
}

pub trait Appraiser: Send + Sync {
    fn rung(&self) -> u8;
    fn appraise<'a>(
        &'a self,
        ctx: AppraiseCtx<'a>,
        ev: &'a Evidence,
    ) -> BoxFuture<'a, Result<Statement, VerifierError>>;
}

/// Rung 1 (ADR-0036 §2.2): the launcher compares what it launched and what the guest reports
/// with the profile's reference values. Attested by its own assertion, or Unattestable. Never
/// Contested: it has no measurement to diverge from (`NeverContested` at rung 1).
pub struct LauncherAssertion;

impl Appraiser for LauncherAssertion {
    fn rung(&self) -> u8 {
        1
    }

    fn appraise<'a>(
        &'a self,
        ctx: AppraiseCtx<'a>,
        ev: &'a Evidence,
    ) -> BoxFuture<'a, Result<Statement, VerifierError>> {
        Box::pin(async move {
            let Evidence::LauncherAssertion { image, persona } = ev else {
                return Err(VerifierError::Malformed("rung 1 appraises the launcher's assertion".into()));
            };
            let p = ctx.profile;
            if image.is_none() || *image != p.image {
                return Err(VerifierError::Malformed("the launched image is not the profile's (P7)".into()));
            }
            if p.persona.model_json_sha256.as_ref() != Some(persona) {
                return Err(VerifierError::Malformed("the guest's Persona is not the profile's (P5, P7)".into()));
            }
            let statement = AppraisalStatement {
                nonce: ctx.nonce.clone(),
                profile: ctx.profile_digest.clone(),
                persona: persona.clone(),
                rung: 1,
                verdict: Appraised::Attested,
                evidence: ev.digest(),
                session_key: None,
                measurement: None,
                tcb: None,
                platform: PLATFORM_LAUNCHER.into(),
            };
            Ok((statement, None))
        })
    }
}

/// A verifier reached over the network, in the RFC 9334 verifier role (T-0045-17). A seam: the
/// reference has none, so it is always unreachable, and that is Unattestable.
pub struct HttpVerifier {
    pub url: String,
}

impl Appraiser for HttpVerifier {
    fn rung(&self) -> u8 {
        3
    }

    fn appraise<'a>(
        &'a self,
        _ctx: AppraiseCtx<'a>,
        _ev: &'a Evidence,
    ) -> BoxFuture<'a, Result<Statement, VerifierError>> {
        Box::pin(async { Err(VerifierError::Unreachable) })
    }
}
