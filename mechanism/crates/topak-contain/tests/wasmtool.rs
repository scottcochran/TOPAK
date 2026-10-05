//! The Run tool host (ADR-0034 A2, pending: P4 for Run is channel fidelity). A tool reaches the
//! target its entry declares and nothing else; a tool that asks for any other capability does not
//! run. The tools here are written in the WebAssembly text format against the host's interface.

use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::TcpListener;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;

use serde_json::json;
use topak_contain::wasmtool::*;
use topak_core::Digest;

/// Connect to the declared target, send the input, return the reply. With no channel, say so.
const ECHO: &str = r#"
(module
  (import "topak" "input_len" (func $input_len (result i32)))
  (import "topak" "input_read" (func $input_read (param i32)))
  (import "topak" "output" (func $output (param i32 i32)))
  (import "topak" "connect" (func $connect (result i32)))
  (import "topak" "send" (func $send (param i32 i32 i32) (result i32)))
  (import "topak" "recv" (func $recv (param i32 i32 i32) (result i32)))
  (memory (export "memory") 1)
  (data (i32.const 2048) "{\"connected\":false}")
  (func (export "run") (result i32)
    (local $n i32) (local $h i32) (local $r i32)
    (local.set $n (call $input_len))
    (call $input_read (i32.const 0))
    (local.set $h (call $connect))
    (if (i32.lt_s (local.get $h) (i32.const 0))
      (then (call $output (i32.const 2048) (i32.const 19)) (return (i32.const 0))))
    (drop (call $send (local.get $h) (i32.const 0) (local.get $n)))
    (local.set $r (call $recv (local.get $h) (i32.const 1024) (i32.const 1000)))
    (call $output (i32.const 1024) (local.get $r))
    (i32.const 0)))
"#;

/// Asks for a socket by address, which the host never grants.
const ROGUE: &str = r#"
(module
  (import "wasi_snapshot_preview1" "sock_open" (func (param i32 i32 i32) (result i32)))
  (memory (export "memory") 1)
  (func (export "run") (result i32) (i32.const 0)))
"#;

const SPIN: &str = r#"
(module
  (memory (export "memory") 1)
  (func (export "run") (result i32) (loop $l (br $l)) (i32.const 0)))
"#;

fn module(name: &str, wat: &str) -> (PathBuf, Digest) {
    let dir = std::env::temp_dir().join(format!("topak-wasmtool-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let path = dir.join(format!("{name}.wasm"));
    std::fs::write(&path, wat::parse_str(wat).unwrap()).unwrap();
    let d = module_digest(&path).unwrap();
    (path, d)
}

/// A target that answers once: it records what it was sent and replies with its length.
fn server() -> (String, std::thread::JoinHandle<Vec<u8>>) {
    let l = TcpListener::bind("127.0.0.1:0").unwrap();
    let addr = l.local_addr().unwrap().to_string();
    let h = std::thread::spawn(move || {
        let (mut s, _) = l.accept().unwrap();
        s.set_read_timeout(Some(Duration::from_secs(2))).unwrap();
        let mut buf = vec![0u8; 4096];
        let n = s.read(&mut buf).unwrap();
        s.write_all(format!("{{\"echo\":{n}}}").as_bytes()).unwrap();
        buf.truncate(n);
        buf
    });
    (addr, h)
}

fn host(tools: Vec<(&str, PathBuf, Digest)>) -> anyhow::Result<Arc<WasmToolHost>> {
    let specs: BTreeMap<String, WasmToolSpec> = tools
        .into_iter()
        .map(|(id, module, module_sha256)| (id.to_string(), WasmToolSpec { module, module_sha256 }))
        .collect();
    Ok(Arc::new(WasmToolHost::new(specs)?))
}

#[tokio::test]
async fn a_run_tool_reaches_its_declared_target_and_nothing_else() {
    let (declared, got) = server();
    // Another listener the tool is not given: it must never see a connection.
    let other = TcpListener::bind("127.0.0.1:0").unwrap();
    other.set_nonblocking(true).unwrap();
    let (path, d) = module("echo", ECHO);
    let ch = Channel { kind: "tcp".into(), target: declared.clone() };
    let h = host(vec![("valve@x", path, d)]).unwrap();

    let inputs = json!({ "open": "v7" }).as_object().unwrap().clone();
    let (result, used) = h.call("valve@x", &inputs, Some(ch)).await.unwrap();
    let sent = serde_json::to_vec(&inputs).unwrap();
    assert_eq!(got.join().unwrap(), sent, "the declared target received the inputs");
    assert_eq!(result, json!({ "echo": sent.len() }));
    assert_eq!((used.connects, used.sent), (1, sent.len() as u64));
    assert!(other.accept().is_err(), "an undeclared listener saw nothing");

    // Build's P4: a call handed no channel gets no network at all. The host holds no target of
    // its own to fall back on (ADR-0049 §5): the same module, the same host, and nothing to reach.
    let (result, used) = h.call("valve@x", &inputs, None).await.unwrap();
    assert_eq!(result, json!({ "connected": false }));
    assert_eq!(used.connects, 0);
}

#[test]
fn a_tool_that_asks_for_any_other_capability_does_not_run() {
    let (path, d) = module("rogue", ROGUE);
    let e = host(vec![("rogue@x", path, d)]).err().expect("refused");
    assert!(format!("{e:#}").contains("not a capability this tool host grants"), "{e:#}");
}

#[test]
fn a_module_that_is_not_the_pinned_one_does_not_load() {
    let (path, _) = module("pinned", ECHO);
    let e = host(vec![("x@y", path, Digest::of(b"another module"))]).err().expect("refused");
    assert!(format!("{e:#}").contains("not the pinned one"), "{e:#}");
}

#[tokio::test]
async fn a_runaway_tool_is_stopped() {
    let (path, d) = module("spin", SPIN);
    let h = host(vec![("spin@x", path, d)]).unwrap();
    let e = h.call("spin@x", &serde_json::Map::new(), None).await.unwrap_err();
    assert!(format!("{e:#}").to_lowercase().contains("fuel"), "{e:#}");
}
