// Layer: implementation · the hand-written half: the generated trait, implemented over topak-core.
// This is where the paper's spec-as-source stops: the wire shape is generated, the rule is not.
use topak_core::state::{Applied, Entry, RenewRequest as CoreRenew};
use topak_lease_v1::operator_server::Operator;
use topak_lease_v1::*;

pub struct OperatorService { node: topak_node::Handle }

#[async_trait::async_trait]
impl Operator for OperatorService {
    async fn renew(&self, req: tonic::Request<RenewRequest>) -> Result<tonic::Response<RenewResponse>, tonic::Status> {
        let r = req.into_inner();
        let core = CoreRenew { seat: r.seat.into(), fence: r.fence, alphabet: kinds(&r.alphabet)?, rung: r.rung as u8, ttl_ms: r.ttl_ms };
        // Ordered through Paxos; `State::apply_renew` runs `Lease::check_renewal` (ADR-0031 §4) at apply.
        let outcome = match self.node.propose(Entry::Renew { id: id(), req: core, appraisal: None }).await {
            Applied::Renewed { fence } => renew_response::Outcome::Lease(self.node.lease(fence).await.into()),
            Applied::Rejected(reason) => renew_response::Outcome::Refused(reason),
            other => return Err(tonic::Status::internal(format!("{other:?}"))),
        };
        Ok(tonic::Response::new(RenewResponse { outcome: Some(outcome) }))
    }
    async fn fence_epoch(&self, _: tonic::Request<FenceEpochRequest>) -> Result<tonic::Response<FenceEpochResponse>, tonic::Status> {
        match self.node.propose(Entry::EpochIncrement { id: id() }).await {
            Applied::EpochIncremented { epoch } => Ok(tonic::Response::new(FenceEpochResponse { epoch })),
            other => Err(tonic::Status::internal(format!("{other:?}"))),
        }
    }
    async fn revoke(&self, req: tonic::Request<RevokeRequest>) -> Result<tonic::Response<RevokeResponse>, tonic::Status> {
        let r = req.into_inner();
        match self.node.propose(Entry::Revoke { id: id(), target: target(r.kind, r.id)? }).await {
            Applied::Revoked { at } => Ok(tonic::Response::new(RevokeResponse { applied_at: at })),
            other => Err(tonic::Status::internal(format!("{other:?}"))),
        }
    }
}
