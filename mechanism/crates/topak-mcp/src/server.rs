//! The MCP front door: the action alphabet, and nothing else, as MCP tools.

use std::sync::Arc;

use rmcp::model::{
    CallToolRequestParams, CallToolResponse, CallToolResult, ContentBlock, ErrorData, InitializeResult, JsonObject,
    ListToolsResult, PaginatedRequestParams, ServerCapabilities, Tool,
};
use rmcp::service::RequestContext;
use rmcp::{RoleServer, ServerHandler};
use serde_json::{Value, json};
use topak_core::Domain;
use topak_core::action::Action;

use crate::proto::{AgentOp, AgentRequest, AgentResponse, SocketClient};

#[derive(Clone)]
pub struct TopakServer {
    client: SocketClient,
    token: Arc<String>,
    domain: Domain,
}

impl TopakServer {
    pub fn new(client: SocketClient, token: String, domain: Domain) -> Self {
        Self { client, token: Arc::new(token), domain }
    }
}

fn schema(v: Value) -> Arc<JsonObject> {
    Arc::new(v.as_object().expect("schema is an object").clone())
}

fn obj(props: Value, required: &[&str]) -> Arc<JsonObject> {
    schema(json!({ "type": "object", "properties": props, "required": required, "additionalProperties": false }))
}

/// The tools for a domain. Their names are the alphabet's; their arguments are the variant's
/// fields. Nothing here grants anything: every call is decided by the mechanism.
pub fn tools_for(domain: Domain) -> Vec<Tool> {
    let digest = json!({ "type": "string", "description": "lowercase hex SHA-256" });
    let invoke_props = json!({
        "tool": { "type": "string" }, "digest": digest, "inputs": { "type": "object" },
    });
    match domain {
        Domain::Build => vec![
            Tool::new(
                "read",
                "Read(ref): resolve a content-addressed object inside the pinned corpus root.",
                obj(json!({ "object": digest }), &["object"]),
            ),
            Tool::new(
                "draft",
                "Draft(target, content): write into this round's workspace.",
                obj(json!({ "target": { "type": "string" }, "content": { "type": "string" } }), &["target", "content"]),
            ),
            Tool::new(
                "invoke",
                "Invoke(tool, inputs): run a tool allowlisted by name and digest. Inputs must be workspace-relative.",
                obj(invoke_props, &["tool", "digest", "inputs"]),
            ),
            Tool::new(
                "emit",
                "Emit(record): append to this principal's round topic.",
                obj(json!({ "record": {} }), &["record"]),
            ),
            Tool::new(
                "submit",
                "Submit(digest): offer the sealed workspace for promotion. Terminal for the round. Omit `artifact` to submit the current workspace.",
                obj(json!({ "artifact": digest }), &[]),
            ),
            Tool::new("abstain", "Submit(⊥): end the authoring round without offering anything.", obj(json!({}), &[])),
            Tool::new(
                "vote",
                "Vote(verdict, digest, evidence, rulesEpoch): cast a promotion vote. Terminal for the round.",
                obj(
                    json!({
                        "verdict": { "type": "string", "enum": ["grant", "deny"] },
                        "artifact": digest, "evidence": digest, "rules_epoch": { "type": "integer", "minimum": 0 },
                    }),
                    &["verdict", "artifact", "evidence", "rules_epoch"],
                ),
            ),
        ],
        Domain::Run => vec![
            Tool::new(
                "run_invoke",
                "RunInvoke(tool, inputs): PROVISIONAL Run action — invoke an allowlisted Run tool.",
                obj(invoke_props, &["tool", "digest", "inputs"]),
            ),
            Tool::new(
                "run_emit",
                "RunEmit(record): PROVISIONAL Run action — append to this principal's round topic.",
                obj(json!({ "record": {} }), &["record"]),
            ),
        ],
    }
}

/// Map a tool call to the typed operation. Syntax only; unknown or malformed calls are errors,
/// never a default action.
pub fn to_op(domain: Domain, name: &str, args: &JsonObject) -> Result<AgentOp, String> {
    let mut a = Value::Object(args.clone());
    let kind = match (domain, name) {
        (Domain::Build, "read") => "Read",
        (Domain::Build, "draft") => "Draft",
        (Domain::Build, "invoke") => "Invoke",
        (Domain::Build, "emit") => "Emit",
        (Domain::Build, "vote") => "Vote",
        (Domain::Run, "run_invoke") => "RunInvoke",
        (Domain::Run, "run_emit") => "RunEmit",
        (Domain::Build, "abstain") => return Ok(AgentOp::Abstain),
        (Domain::Build, "submit") => match args.get("artifact") {
            None => return Ok(AgentOp::SubmitWorkspace),
            Some(_) => "Submit",
        },
        _ => return Err(format!("no such tool: {name}")),
    };
    a["kind"] = Value::String(kind.to_string());
    let action: Action = serde_json::from_value(a).map_err(|e| format!("bad arguments for {name}: {e}"))?;
    Ok(AgentOp::Act { action })
}

impl ServerHandler for TopakServer {
    fn get_info(&self) -> InitializeResult {
        InitializeResult::new(ServerCapabilities::builder().enable_tools().build()).with_instructions(
            "TOPAK mechanism front door. Every tool is one action of your alphabet; each is fenced, \
             checked against the policy floor and bundle, ordered by consensus, and only then performed.",
        )
    }

    async fn list_tools(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, ErrorData> {
        Ok(ListToolsResult::with_all_items(tools_for(self.domain)))
    }

    async fn call_tool(
        &self,
        request: CallToolRequestParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, ErrorData> {
        let args = request.arguments.clone().unwrap_or_default();
        let op = match to_op(self.domain, &request.name, &args) {
            Ok(op) => op,
            Err(e) => return Err(ErrorData::invalid_params(e, None)),
        };
        let req = AgentRequest { token: (*self.token).clone(), op };
        let resp: AgentResponse = self
            .client
            .request(&req)
            .await
            .map_err(|e| ErrorData::internal_error(format!("mechanism unreachable: {e}"), None))?;
        let text = ContentBlock::text(serde_json::to_string_pretty(&resp.detail).unwrap_or_default());
        Ok(if resp.admitted { CallToolResult::success(vec![text]) } else { CallToolResult::error(vec![text]) }.into())
    }
}
