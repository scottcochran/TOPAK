//! Downstream tools for `Invoke` and `Actuate`, reached as MCP servers over stdio.
//!
//! An allowlist entry is `name@digest` (ADR-0022 §3). The baseline defines the digest as
//! `SHA-256(binary digest ‖ canonical JSON of the tool's MCP input schema)`, so a different
//! binary or a changed interface is a different tool. Both halves are checked on every call:
//! the binary's bytes before it is spawned, the schema from the spawned server's `tools/list`.
//!
//! What is **not** checked: hermeticity for a Build tool (ADR-0022 §3's per-entry obligation,
//! assumption A2), or channel fidelity for a Run tool (ADR-0042 §6: that it opens the channel
//! its entry declares and no other).
//! The child runs with a cleared environment and the workspace as its working directory, and
//! nothing more. A tool that opens a socket collapses the envelope; nothing here can see it.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::{Context as _, bail};
use rmcp::ServiceExt;
use rmcp::model::{CallToolRequestParams, JsonObject};
use rmcp::transport::{ConfigureCommandExt, TokioChildProcess};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use topak_core::Digest;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ToolSpec {
    /// Executable path.
    pub command: PathBuf,
    #[serde(default)]
    pub args: Vec<String>,
    /// SHA-256 of the executable's bytes.
    pub binary_sha256: Digest,
    /// The tool's name on the downstream MCP server.
    pub mcp_tool: String,
}

pub fn tool_digest(binary: &Digest, input_schema: &Value) -> Digest {
    let mut bytes = binary.0.clone().into_bytes();
    bytes.push(0);
    bytes.extend(topak_core::canonical_json(input_schema));
    Digest::of(&bytes)
}

#[derive(Default)]
pub struct ToolHost {
    /// Keyed by allowlist id, `name@digest`.
    pub specs: BTreeMap<String, ToolSpec>,
}

impl ToolHost {
    pub fn new(specs: BTreeMap<String, ToolSpec>) -> Self {
        Self { specs }
    }

    /// Spawn the tool, pin it, and call it once. `cwd` is the workspace.
    pub async fn call(&self, tool_id: &str, inputs: &JsonObject, cwd: &Path) -> anyhow::Result<Value> {
        let spec = self.specs.get(tool_id).with_context(|| format!("no tool host entry for {tool_id}"))?;
        let (_, want) = tool_id.rsplit_once('@').context("tool id is name@digest")?;
        let bin = Digest::of(&std::fs::read(&spec.command)?);
        if bin != spec.binary_sha256 {
            bail!("binary digest {} is not the pinned {}", bin.short(), spec.binary_sha256.short());
        }
        let cmd = tokio::process::Command::new(&spec.command).configure(|c| {
            c.args(&spec.args).current_dir(cwd).env_clear();
        });
        let client = ().serve(TokioChildProcess::new(cmd)?).await?;
        let result = async {
            let tools = client.list_all_tools().await?;
            let tool = tools
                .iter()
                .find(|t| t.name == spec.mcp_tool)
                .with_context(|| format!("server does not offer {}", spec.mcp_tool))?;
            let got = tool_digest(&bin, &Value::Object((*tool.input_schema).clone()));
            if got.0 != want {
                bail!("tool digest {} is not the allowlisted {}", got.short(), &want[..want.len().min(16)]);
            }
            let r = client
                .call_tool(CallToolRequestParams::new(spec.mcp_tool.clone()).with_arguments(inputs.clone()))
                .await?;
            Ok(serde_json::to_value(r)?)
        }
        .await;
        let _ = client.cancel().await;
        result
    }

    /// Compute the allowlist digest for a tool (operator helper).
    pub async fn digest_of(command: &Path, args: &[String], mcp_tool: &str) -> anyhow::Result<(Digest, Digest)> {
        let bin = Digest::of(&std::fs::read(command)?);
        let cmd = tokio::process::Command::new(command).configure(|c| {
            c.args(args).env_clear();
        });
        let client = ().serve(TokioChildProcess::new(cmd)?).await?;
        let tools = client.list_all_tools().await?;
        let _ = client.cancel().await;
        let tool = tools.iter().find(|t| t.name == mcp_tool).with_context(|| format!("no tool {mcp_tool}"))?;
        Ok((bin.clone(), tool_digest(&bin, &Value::Object((*tool.input_schema).clone()))))
    }
}
