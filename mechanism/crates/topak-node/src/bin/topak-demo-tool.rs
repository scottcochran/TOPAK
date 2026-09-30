//! A hermetic demo tool for `Invoke`: `wordcount(path)` counts lines, words and bytes of a
//! workspace-relative file. No network, no filesystem outside its working directory,
//! deterministic given its inputs — the ADR-0022 §3 obligation, met by construction here and
//! by nobody's check.
//!
//! `sleep(ms)` waits and returns. It stands in for a Run tool in the end-to-end tests: fast with
//! `ms = 0`, and slow enough with a larger value for a round to seal while the call is in flight
//! (ADR-0042 §3, the `unknown` record). It opens no channel, so it is a Run tool in name only.

use std::sync::Arc;

use rmcp::model::{
    CallToolRequestParams, CallToolResponse, CallToolResult, ContentBlock, ErrorData, InitializeResult,
    ListToolsResult, PaginatedRequestParams, ServerCapabilities, Tool,
};
use rmcp::service::RequestContext;
use rmcp::{RoleServer, ServerHandler, ServiceExt};
use serde_json::json;

struct Demo;

impl ServerHandler for Demo {
    fn get_info(&self) -> InitializeResult {
        InitializeResult::new(ServerCapabilities::builder().enable_tools().build())
    }

    async fn list_tools(
        &self,
        _r: Option<PaginatedRequestParams>,
        _c: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, ErrorData> {
        let schema = json!({
            "type": "object",
            "properties": { "path": { "type": "string" } },
            "required": ["path"],
            "additionalProperties": false,
        });
        let sleep = json!({
            "type": "object",
            "properties": { "ms": { "type": "integer", "minimum": 0 } },
            "required": ["ms"],
            "additionalProperties": false,
        });
        Ok(ListToolsResult::with_all_items(vec![
            Tool::new(
                "wordcount",
                "Count lines, words and bytes of a workspace file.",
                Arc::new(schema.as_object().unwrap().clone()),
            ),
            Tool::new("sleep", "Wait for `ms` milliseconds.", Arc::new(sleep.as_object().unwrap().clone())),
        ]))
    }

    async fn call_tool(
        &self,
        req: CallToolRequestParams,
        _c: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, ErrorData> {
        if req.name == "sleep" {
            let ms = req
                .arguments
                .as_ref()
                .and_then(|a| a.get("ms"))
                .and_then(|m| m.as_u64())
                .ok_or_else(|| ErrorData::invalid_params("ms is required", None))?;
            tokio::time::sleep(std::time::Duration::from_millis(ms)).await;
            let out = json!({ "slept": ms });
            return Ok(CallToolResult::success(vec![ContentBlock::text(out.to_string())]).into());
        }
        let path = req
            .arguments
            .as_ref()
            .and_then(|a| a.get("path"))
            .and_then(|p| p.as_str())
            .ok_or_else(|| ErrorData::invalid_params("path is required", None))?;
        if path.starts_with('/') || path.split('/').any(|c| c == "..") {
            return Err(ErrorData::invalid_params("path must be workspace-relative", None));
        }
        let text = std::fs::read_to_string(path).map_err(|e| ErrorData::invalid_params(e.to_string(), None))?;
        let out =
            json!({ "lines": text.lines().count(), "words": text.split_whitespace().count(), "bytes": text.len() });
        Ok(CallToolResult::success(vec![ContentBlock::text(out.to_string())]).into())
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> anyhow::Result<()> {
    Demo.serve(rmcp::transport::stdio()).await?.waiting().await?;
    Ok(())
}
