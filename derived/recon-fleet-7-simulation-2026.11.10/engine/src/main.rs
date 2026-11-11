//! Evaluates compiled TOPAK bundles with opa-wasm, the engine `topak-bundle` uses.
//!
//!     recon7-engine name=policy.wasm:data.json ...
//!
//! Reads one JSON request per line on stdin, `{"b": bundle, "e": entrypoint, "i": input}`, and writes
//! `{"r": result}` or `{"err": message}` per line on stdout. An error is reported and never read as
//! an allow.
use std::collections::HashMap;
use std::io::{BufRead, Write};

use opa_wasm::wasmtime::{Config, Engine, Module, Store};
use opa_wasm::{DefaultContext, Policy, Runtime};
use serde_json::{json, Value};

struct Compiled {
    store: Store<()>,
    policy: Policy<DefaultContext>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let mut bundles = HashMap::new();
    for arg in std::env::args().skip(1) {
        let (name, paths) = arg.split_once('=').expect("name=policy.wasm:data.json");
        let (wasm, data) = paths.split_once(':').expect("policy.wasm:data.json");
        let engine = Engine::new(&Config::new())?;
        let module = Module::new(&engine, std::fs::read(wasm)?)?;
        let mut store = Store::new(&engine, ());
        let runtime = Runtime::new(&mut store, &module).await?;
        let data: Value = serde_json::from_str(&std::fs::read_to_string(data)?)?;
        let policy = runtime.with_data(&mut store, &data).await?;
        bundles.insert(name.to_string(), Compiled { store, policy });
    }
    let stdin = std::io::stdin();
    let mut out = std::io::stdout().lock();
    for line in stdin.lock().lines() {
        let req: Value = serde_json::from_str(&line?)?;
        let reply = match bundles.get_mut(req["b"].as_str().unwrap_or("")) {
            None => json!({"err": "no such bundle"}),
            Some(c) => {
                let entry = req["e"].as_str().unwrap_or("");
                let res: anyhow::Result<Value> = c.policy.evaluate(&mut c.store, entry, &req["i"]).await;
                match res {
                    Ok(v) => json!({"r": v}),
                    Err(e) => json!({"err": e.to_string()}),
                }
            }
        };
        writeln!(out, "{reply}")?;
        out.flush()?;
    }
    Ok(())
}
