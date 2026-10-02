//! A scripted occupant (ADR-0036 §3) for the launcher's tests: it plays one Build round through
//! the one channel and holds no token. It is the shape `serve.py --occupant` will have, with no
//! model: the Persona bundle is a `model.json` naming a weights file by digest.
//!
//! ```text
//! topak-demo-guest --model <model.json> [--rung N] [--read <digest>]
//!                  [--script read,draft,emit,submit] [--exit] [--rogue]
//! ```
//!
//! - It checks the weights against `model.json` and exits 3 before its identity line on a
//!   mismatch (ADR-0036 §2.1, §7's second refusal).
//! - At rung 2 or 3 it makes a session key pair, names the public key in its identity line,
//!   binds it with each nonce, and signs every action under it (ADR-0034 §3.5).
//! - After its script it waits for shutdown, answering attestation requests, unless `--exit`, in
//!   which case it closes its channel. `--rogue` changes nothing it does; the simulated platform
//!   measures the argument, which is the point.

use std::io::{BufRead, Write};
use std::path::PathBuf;

use serde_json::{Value, json};
use topak_contain::guest::{GuestEvidence, GuestHello, GuestMsg, HostMsg};
use topak_core::action::Action;
use topak_core::authentic;
use topak_core::confine::{AGENT_OP_PURPOSE, SessionProof, report_data, session_body};
use topak_core::{Digest, Epoch, LogIndex};
use topak_mcp::proto::{AgentOp, AgentResponse};

struct Args {
    model: PathBuf,
    rung: u8,
    read: Option<Digest>,
    script: Vec<String>,
    exit: bool,
}

fn args() -> Args {
    let mut a = Args { model: PathBuf::new(), rung: 1, read: None, script: vec![], exit: false };
    let mut it = std::env::args().skip(1);
    while let Some(k) = it.next() {
        match k.as_str() {
            "--model" => a.model = it.next().expect("--model <path>").into(),
            "--rung" => a.rung = it.next().expect("--rung <n>").parse().expect("a rung"),
            "--read" => a.read = Some(Digest(it.next().expect("--read <digest>"))),
            "--script" => a.script = it.next().expect("--script a,b").split(',').map(String::from).collect(),
            "--exit" => a.exit = true,
            "--rogue" => {}
            other => {
                eprintln!("unknown argument {other}");
                std::process::exit(2)
            }
        }
    }
    a
}

struct Guest {
    out: std::io::Stdout,
    lines: std::io::Lines<std::io::StdinLock<'static>>,
    secret: Option<[u8; 32]>,
    key: Option<String>,
    lease: Option<(LogIndex, Epoch)>,
    ctr: u64,
}

impl Guest {
    fn send(&mut self, m: &GuestMsg) {
        let mut l = serde_json::to_vec(m).unwrap();
        l.push(b'\n');
        if self.out.write_all(&l).and_then(|_| self.out.flush()).is_err() {
            std::process::exit(0);
        }
    }

    /// Read until a response arrives, answering what the host starts. `None`: shut down.
    fn next(&mut self) -> Option<AgentResponse> {
        loop {
            let line = match self.lines.next() {
                Some(Ok(l)) => l,
                _ => return None,
            };
            let msg: HostMsg = match serde_json::from_str(&line) {
                Ok(m) => m,
                Err(e) => {
                    eprintln!("not a host message: {e}");
                    return None;
                }
            };
            match msg {
                HostMsg::Attest { nonce } => {
                    let rd = report_data(&nonce, self.key.as_ref());
                    self.send(&GuestMsg::Evidence(GuestEvidence { report_data: rd }));
                }
                HostMsg::Granted { fence, epoch } => {
                    eprintln!("granted at fence {fence}, epoch {epoch}");
                    let first = self.lease.is_none();
                    self.lease = Some((fence, epoch));
                    if first {
                        return Some(AgentResponse { admitted: true, detail: json!({ "granted": fence }) });
                    }
                }
                HostMsg::Response { response } => return Some(response),
                HostMsg::Shutdown => return None,
            }
        }
    }

    fn act(&mut self, op: AgentOp) -> Option<AgentResponse> {
        let proof = match (&self.secret, self.lease) {
            (Some(sk), Some((fence, epoch))) => {
                self.ctr += 1;
                let d = Digest::of_json(&op);
                let sig = authentic::sign(AGENT_OP_PURPOSE, &session_body(fence, epoch, self.ctr, &d), sk).sig;
                Some(SessionProof { ctr: self.ctr, op: d, sig })
            }
            _ => None,
        };
        self.send(&GuestMsg::Op { op, proof });
        self.next()
    }
}

fn main() {
    let a = args();
    let bytes = std::fs::read(&a.model).unwrap_or_else(|e| {
        eprintln!("no Persona bundle at {}: {e}", a.model.display());
        std::process::exit(3)
    });
    let model: Value = serde_json::from_slice(&bytes).unwrap_or_else(|_| std::process::exit(3));
    let weights = a.model.parent().unwrap().join(model["weights"].as_str().unwrap_or("weights.bin"));
    let ok = std::fs::read(&weights).is_ok_and(|w| Some(Digest::of(&w).0.as_str()) == model["weights_sha256"].as_str());
    if !ok {
        // ADR-0036 §2.1: a guest that cannot verify its bundle exits without its identity line.
        eprintln!("the weights do not match model.json");
        std::process::exit(3)
    }
    let persona = Digest::of(&bytes);
    let secret: Option<[u8; 32]> = (a.rung >= 2).then(rand::random);
    let key = secret.map(|s| authentic::sign("key", &Value::Null, &s).key);
    let mut g = Guest {
        out: std::io::stdout(),
        lines: std::io::stdin().lock().lines(),
        secret,
        key: key.clone(),
        lease: None,
        ctr: 0,
    };
    g.send(&GuestMsg::Hello(GuestHello {
        persona: persona.clone(),
        family: model["family"].as_str().unwrap_or("demo").into(),
        params: model["params"].as_u64().unwrap_or(0),
        root: "demo".into(),
        session_key: key,
    }));
    // Nothing to do until the lease exists: the launcher appraises first.
    if g.next().is_none() {
        return;
    }
    for step in a.script.clone() {
        let op = match step.as_str() {
            "read" => AgentOp::Act { action: Action::Read { object: a.read.clone().expect("--read for a read step") } },
            "draft" => AgentOp::Act {
                action: Action::Draft {
                    target: "notes.md".into(),
                    content: format!("drafted by the occupant under Persona {}\n", persona.short()),
                },
            },
            "emit" => AgentOp::Act { action: Action::Emit { record: json!({ "note": "occupant" }) } },
            "submit" => AgentOp::SubmitWorkspace,
            other => {
                eprintln!("unknown step {other}");
                std::process::exit(2)
            }
        };
        match g.act(op) {
            Some(r) => eprintln!("{step}: admitted={} {}", r.admitted, r.detail),
            None => return,
        }
    }
    if a.exit {
        return;
    }
    while g.next().is_some() {}
}
