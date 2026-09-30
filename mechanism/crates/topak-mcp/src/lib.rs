//! MCP at both edges of the mechanism.
//!
//! - **Front door** ([`server`]): an agent's *only* interface is an MCP server whose tools are
//!   exactly the seat's alphabet (Build: ADR-0022 §1; Run: ADR-0040 §1, Proposed). Each tool
//!   call becomes one typed `Action`, sent to the node, which fences, lifts, runs the floor and
//!   the bundle, orders the admit through Paxos and only then performs the effect. The agent
//!   never touches the filesystem, the tools or Kafka itself.
//! - **Back door** ([`toolhost`]): `Invoke` and `Actuate` effects call allowlisted downstream MCP
//!   tools, pinned by binary digest and by tool-schema digest.
//!
//! Neither edge confines anything. An agent process with a shell can bypass the front door
//! entirely; that is the sandbox gap (ADR-0022 §6), and every lease is issued at rung 0.

pub mod proto;
pub mod server;
pub mod toolhost;
