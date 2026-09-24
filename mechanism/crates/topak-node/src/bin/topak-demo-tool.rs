//! A hermetic demo tool for `Invoke`: `wordcount(path)` counts lines, words and bytes of a
//! workspace-relative file. No network, no filesystem outside its working directory,
//! deterministic given its inputs — the ADR-0022 §3 obligation, met by construction here and
//! by nobody's check.

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
        Ok(ListToolsResult::with_all_items(vec![Tool::new(
            "wordcount",
            "Count lines, words and bytes of a workspace file.",
            Arc::new(schema.as_object().unwrap().clone()),
        )]))
    }

    async fn call_tool(
        &self,
        req: CallToolRequestParams,
        _c: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, ErrorData> {
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
