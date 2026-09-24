//! `topak` — run a mechanism replica, its MCP front door, and operator helpers.

use std::io::Read;
use std::path::PathBuf;

use clap::{Parser, Subcommand};
use ed25519_dalek::{Signer, SigningKey};
use rmcp::ServiceExt;
use serde_json::Value;
use topak_core::Domain;
use topak_core::authentic::{Signed, signing_bytes};
use topak_mcp::proto::SocketClient;
use topak_mcp::server::TopakServer;
use topak_mcp::toolhost::ToolHost;
use topak_node::config::NodeConfig;

#[derive(Parser)]
#[command(name = "topak", about = "TOPAK admit-path reference mechanism")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Run one replica.
    Node {
        #[arg(long)]
        config: PathBuf,
    },
    /// Serve the MCP front door on stdio for one session (launch this as the agent's MCP server).
    Mcp {
        #[arg(long)]
        socket: PathBuf,
        #[arg(long)]
        token: String,
        #[arg(long, default_value = "build")]
        domain: String,
    },
    /// Send one operator request (JSON argument, or `-` for stdin) and print the reply.
    Op {
        #[arg(long)]
        socket: PathBuf,
        request: String,
    },
    /// Generate an Ed25519 key pair (hex).
    Keygen,
    /// Sign a JSON body for a purpose (`issuance`, `break-glass`).
    Sign {
        #[arg(long)]
        purpose: String,
        #[arg(long)]
        secret: String,
        /// JSON file, or `-` for stdin.
        body: String,
    },
    /// Compute a downstream tool's allowlist id (`name@digest`).
    ToolDigest {
        #[arg(long)]
        command: PathBuf,
        #[arg(long)]
        tool: String,
        #[arg(last = true)]
        args: Vec<String>,
    },
    /// Check a rules file against the rules floor.
    CheckRules { rules: PathBuf },
}

fn read_arg(s: &str) -> anyhow::Result<String> {
    if s == "-" {
        let mut b = String::new();
        std::io::stdin().read_to_string(&mut b)?;
        Ok(b)
    } else if std::path::Path::new(s).exists() {
        Ok(std::fs::read_to_string(s)?)
    } else {
        Ok(s.to_string())
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    // Logs go to stderr: stdout belongs to MCP in `topak mcp`.
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_env_filter(tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .init();
    match cli.cmd {
        Cmd::Node { config } => {
            let cfg = NodeConfig::load(&config)?;
            let id = cfg.id;
            topak_node::start_node(cfg).await?;
            tracing::info!(replica = id, "running");
            tokio::signal::ctrl_c().await?;
        }
        Cmd::Mcp { socket, token, domain } => {
            let domain = match domain.as_str() {
                "build" => Domain::Build,
                "run" => Domain::Run,
                d => anyhow::bail!("unknown domain {d}"),
            };
            let server = TopakServer::new(SocketClient::new(socket), token, domain);
            server.serve(rmcp::transport::stdio()).await?.waiting().await?;
        }
        Cmd::Op { socket, request } => {
            let req: Value = serde_json::from_str(&read_arg(&request)?)?;
            let resp: Value = SocketClient::new(socket).request(&req).await?;
            println!("{}", serde_json::to_string_pretty(&resp)?);
        }
        Cmd::Keygen => {
            let sk = SigningKey::generate(&mut rand::rngs::OsRng);
            println!(
                "{}",
                serde_json::json!({
                    "public": hex::encode(sk.verifying_key().to_bytes()),
                    "secret": hex::encode(sk.to_bytes()),
                })
            );
        }
        Cmd::Sign { purpose, secret, body } => {
            let body: Value = serde_json::from_str(&read_arg(&body)?)?;
            let bytes: [u8; 32] = hex::decode(secret)?.try_into().map_err(|_| anyhow::anyhow!("secret is 32 bytes"))?;
            let sk = SigningKey::from_bytes(&bytes);
            let sig = sk.sign(&signing_bytes(&purpose, &body));
            let s = Signed { key: hex::encode(sk.verifying_key().to_bytes()), sig: hex::encode(sig.to_bytes()) };
            println!("{}", serde_json::to_string(&s)?);
        }
        Cmd::ToolDigest { command, tool, args } => {
            let (bin, digest) = ToolHost::digest_of(&command, &args, &tool).await?;
            println!("{}", serde_json::json!({ "id": format!("{tool}@{digest}"), "binary_sha256": bin }));
        }
        Cmd::CheckRules { rules } => {
            let floor = topak_floor::Floor::load()?;
            match topak_node::genesis(&rules, &floor) {
                Ok(_) => println!("rules satisfy the rules floor (R1 R2 R5 R6 R7 R9)"),
                Err(e) => {
                    eprintln!("{e}");
                    std::process::exit(1);
                }
            }
        }
    }
    Ok(())
}
