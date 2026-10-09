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
    /// The tool list the mechanism gave this session's lease (ADR-0048 §2), as rendered.
    tool_list: Option<Arc<Value>>,
}

impl TopakServer {
    pub fn new(client: SocketClient, token: String, domain: Domain) -> Self {
        Self { client, token: Arc::new(token), domain, tool_list: None }
    }

    /// Ask the mechanism for this session's tool list, once, so that it is delivered with the
    /// server's instructions when the principal connects. The list is the mechanism's, passed on
    /// as rendered: this front door describes the alphabet and no tool.
    pub async fn with_tool_list(mut self) -> anyhow::Result<Self> {
        let req = AgentRequest { token: (*self.token).clone(), op: AgentOp::ToolList };
        let resp: AgentResponse = self.client.request(&req).await?;
        anyhow::ensure!(resp.admitted, "the mechanism gave no tool list: {}", resp.detail);
        self.tool_list = Some(Arc::new(resp.detail["tool_list"].clone()));
        Ok(self)
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
                "consult",
                "Consult(ref): resolve a content-addressed object inside the pinned Run root. Not an effect.",
                obj(json!({ "object": digest }), &["object"]),
            ),
            Tool::new(
                "actuate",
                "Actuate(tool, inputs): invoke a Run tool allowlisted by name and digest. Every call is recorded on this round's topic.",
                obj(invoke_props, &["tool", "digest", "inputs"]),
            ),
            Tool::new(
                "report",
                "Report(record): append to this principal's round topic.",
                obj(json!({ "record": {} }), &["record"]),
            ),
            // ADR-0040 A2 (pending, with ADR-0054): held only by an `orchestrator` seat.
            Tool::new(
                "route",
                "Route(edge): an orchestrator's choice of one chosen edge out of the decision point its round was granted for. The mechanism checks that the edge is enabled, and checks it again where the route is applied.",
                obj(json!({ "edge": { "type": "string" } }), &["edge"]),
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
        (Domain::Run, "consult") => "Consult",
        (Domain::Run, "actuate") => "Actuate",
        (Domain::Run, "report") => "Report",
        (Domain::Run, "route") => "Route",
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
        let mut text = String::from(
            "TOPAK mechanism front door. Every tool is one action of your alphabet; each is fenced, \
             checked against the policy floor and bundle, ordered by consensus, and only then performed.",
        );
        if let Some(list) = &self.tool_list {
            let verb = if self.domain == Domain::Build { "invoke" } else { "actuate" };
            text.push_str(&format!(
                "\n\nThe tools you may call with `{verb}` this round, by the name and digest given here. \
                 This list is the mechanism's and is the only description of them with standing:\n{list}"
            ));
        }
        InitializeResult::new(ServerCapabilities::builder().enable_tools().build()).with_instructions(text)
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
