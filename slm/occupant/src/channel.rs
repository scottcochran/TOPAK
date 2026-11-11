//! The occupant's one way out. Two transports carry the same three operations.
//!
//! `Stdio` is the launcher's channel at rung 1 (`mechanism/crates/topak-contain/src/guest.rs`): the
//! guest speaks first with its identity, answers `attest` whenever it arrives, waits for
//! `granted`, then sends token-less `op` lines and reads one `response` each. No token crosses it.
//!
//! `Mcp` is the host-run occupant at rung 0 (`slm/serve/profile-host-rung0.json`): the occupant
//! holds the session token itself and drives `topak mcp`, the agent socket's stdio front, as
//! `slm/rehearsal/drive.py` does. The image carries no `topak` binary, so it is unreachable there.

use std::io::{BufRead, BufReader, Read, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio as PStdio};

use serde_json::{json, Value};

use crate::bundle::sha256_hex;

/// A line longer than this ends the round: `Read` content is the only large thing on the channel.
pub const MAX_LINE: usize = 8 << 20;

pub enum Op {
    Read { object: String },
    Draft { target: String, content: String },
    Submit,
}

pub struct Reply {
    pub admitted: bool,
    pub detail: Value,
}

pub trait Channel {
    /// `None`: the other side ended the round (shutdown or closed).
    fn act(&mut self, op: &Op) -> Option<Reply>;
}

/// Read one line of at most `MAX_LINE` bytes. `Ok(None)` at end of stream.
pub fn read_line(r: &mut impl BufRead) -> Result<Option<String>, String> {
    let mut buf = Vec::new();
    loop {
        let avail = r.fill_buf().map_err(|e| e.to_string())?;
        if avail.is_empty() {
            return if buf.is_empty() { Ok(None) } else { Err("stream ended inside a line".into()) };
        }
        let (take, done) = match avail.iter().position(|&b| b == b'\n') {
            Some(i) => (i + 1, true),
            None => (avail.len(), false),
        };
        if buf.len() + take > MAX_LINE + 1 {
            return Err(format!("a line longer than {MAX_LINE} bytes"));
        }
        buf.extend_from_slice(&avail[..take]);
        r.consume(take);
        if done {
            buf.pop();
            return String::from_utf8(buf).map(Some).map_err(|_| "a line that is not UTF-8".into());
        }
    }
}

pub struct Stdio<R: BufRead, W: Write> {
    input: R,
    out: W,
    granted: Option<(u64, u64)>,
}

/// `report_data` at rungs 0 and 1: the digest of `{"nonce", "sessionKey": null}` in canonical JSON
/// (sorted keys, no spaces), as `topak-core::confine` computes it. At rung 1 the launcher does not
/// check it, but a guest that does not answer is not attested.
pub fn report_data(nonce: &str) -> String {
    sha256_hex(json!({ "nonce": nonce, "sessionKey": null }).to_string().as_bytes())
}

impl<R: BufRead, W: Write> Stdio<R, W> {
    pub fn new(input: R, out: W) -> Self {
        Stdio { input, out, granted: None }
    }

    pub fn send(&mut self, m: &Value) {
        let mut l = serde_json::to_vec(m).expect("serializable");
        l.push(b'\n');
        if self.out.write_all(&l).and_then(|_| self.out.flush()).is_err() {
            eprintln!("occupant: the channel closed");
            std::process::exit(0);
        }
    }

    pub fn hello(&mut self, persona: &str, family: &str, params: u64, root: &str) {
        self.send(&json!({ "msg": "hello", "persona": persona, "family": family, "params": params,
                           "root": root, "session_key": null }));
    }

    /// Read until a response arrives, answering what only the host starts. The first `granted`
    /// counts as a response (the lease exists); later ones are renewals.
    fn next(&mut self) -> Option<Reply> {
        loop {
            let line = match read_line(&mut self.input) {
                Ok(Some(l)) => l,
                Ok(None) => return None,
                Err(e) => {
                    eprintln!("occupant: {e}");
                    std::process::exit(4);
                }
            };
            let m: Value = match serde_json::from_str(&line) {
                Ok(m) => m,
                Err(e) => {
                    eprintln!("occupant: not a host message: {e}");
                    std::process::exit(4);
                }
            };
            match m["msg"].as_str() {
                Some("attest") => {
                    let rd = report_data(m["nonce"].as_str().unwrap_or(""));
                    self.send(&json!({ "msg": "evidence", "report_data": rd }));
                }
                Some("granted") => {
                    let lease = (m["fence"].as_u64().unwrap_or(0), m["epoch"].as_u64().unwrap_or(0));
                    eprintln!("occupant: granted at fence {}, epoch {}", lease.0, lease.1);
                    let first = self.granted.is_none();
                    self.granted = Some(lease);
                    if first {
                        return Some(Reply { admitted: true, detail: json!({ "granted": lease.0 }) });
                    }
                }
                Some("response") => {
                    let r = &m["response"];
                    return Some(Reply { admitted: r["admitted"].as_bool().unwrap_or(false), detail: r["detail"].clone() });
                }
                Some("shutdown") => return None,
                other => {
                    eprintln!("occupant: unknown host message {other:?}");
                    std::process::exit(4);
                }
            }
        }
    }

    /// Nothing to do until the lease exists: the launcher appraises first.
    pub fn wait_for_lease(&mut self) -> bool {
        self.next().is_some()
    }

    /// After the round: answer the host until it shuts the guest down or closes the channel.
    pub fn drain(&mut self) {
        while self.next().is_some() {}
    }
}

impl<R: BufRead, W: Write> Channel for Stdio<R, W> {
    fn act(&mut self, op: &Op) -> Option<Reply> {
        let op = match op {
            Op::Read { object } => json!({ "op": "act", "action": { "kind": "Read", "object": object } }),
            Op::Draft { target, content } => {
                json!({ "op": "act", "action": { "kind": "Draft", "target": target, "content": content } })
            }
            Op::Submit => json!({ "op": "submit_workspace" }),
        };
        self.send(&json!({ "msg": "op", "op": op, "proof": null }));
        self.next()
    }
}

pub struct Mcp {
    child: Child,
    w: ChildStdin,
    r: BufReader<ChildStdout>,
    n: u64,
}

impl Mcp {
    pub fn start(topak: &str, socket: &str, token: &str) -> Result<Mcp, String> {
        let mut child = Command::new(topak)
            .args(["mcp", "--socket", socket, "--token", token, "--domain", "build"])
            .stdin(PStdio::piped())
            .stdout(PStdio::piped())
            .stderr(PStdio::null())
            .spawn()
            .map_err(|e| format!("cannot start {topak} mcp: {e}"))?;
        let w = child.stdin.take().unwrap();
        let r = BufReader::new(child.stdout.take().unwrap());
        let mut m = Mcp { child, w, r, n: 0 };
        m.rpc("initialize", json!({ "protocolVersion": "2025-06-18", "capabilities": {},
                                   "clientInfo": { "name": "topak-slm-occupant", "version": "0" } }))?;
        m.send(&json!({ "jsonrpc": "2.0", "method": "notifications/initialized" }))?;
        Ok(m)
    }

    fn send(&mut self, m: &Value) -> Result<(), String> {
        let mut l = serde_json::to_vec(m).unwrap();
        l.push(b'\n');
        self.w.write_all(&l).and_then(|_| self.w.flush()).map_err(|e| e.to_string())
    }

    fn rpc(&mut self, method: &str, params: Value) -> Result<Value, String> {
        self.n += 1;
        let id = self.n;
        self.send(&json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": params }))?;
        loop {
            let line = read_line(&mut self.r)?.ok_or("topak mcp closed its stdout")?;
            let m: Value = serde_json::from_str(&line).map_err(|e| e.to_string())?;
            if m["id"].as_u64() == Some(id) {
                return Ok(m);
            }
        }
    }

    pub fn close(mut self) {
        drop(self.w);
        let mut rest = String::new();
        let _ = self.r.read_to_string(&mut rest);
        let _ = self.child.wait();
    }
}

impl Channel for Mcp {
    fn act(&mut self, op: &Op) -> Option<Reply> {
        let (name, args) = match op {
            Op::Read { object } => ("read", json!({ "object": object })),
            Op::Draft { target, content } => ("draft", json!({ "target": target, "content": content })),
            Op::Submit => ("submit", json!({})),
        };
        let r = match self.rpc("tools/call", json!({ "name": name, "arguments": args })) {
            Ok(r) => r,
            Err(e) => {
                eprintln!("occupant: {e}");
                return None;
            }
        };
        if !r["error"].is_null() {
            return Some(Reply { admitted: false, detail: r["error"].clone() });
        }
        let res = &r["result"];
        let text = res["content"][0]["text"].as_str().unwrap_or("null");
        let detail = serde_json::from_str(text).unwrap_or(Value::String(text.into()));
        Some(Reply { admitted: !res["isError"].as_bool().unwrap_or(false), detail })
    }
}
