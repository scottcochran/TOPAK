//! The Run tool host (ADR-0034 A2, pending: P4 for Run is channel fidelity). A Run tool runs on the
//! mechanism's side of the front door as a Wasm module instantiated per call, and the only network
//! capability it is handed is a connection to the target its allowlist entry declares. It cannot
//! name another: the import takes no address. Fidelity holds by construction, a check and not a
//! trust, so ADR-0045 T-0045-24 is delegated to this runtime (T-0045-25) rather than excluded.
//!
//! PROVISIONAL (tool-abi). A2 says a Wasm *component* with a scoped socket capability. The build
//! host has no `wasm32-wasip2` target, so the reference uses a core module and this host
//! interface, which grants strictly less: no filesystem, no clock, no entropy, one connection.
//!
//! ```text
//! imports (module "topak")            exports
//!   input_len() -> i32                  memory
//!   input_read(ptr)                     run() -> i32      0: ok, the output is the result
//!   output(ptr, len)
//!   connect() -> i32                    a handle to the declared target, or -1
//!   send(handle, ptr, len) -> i32       bytes written, or -1
//!   recv(handle, ptr, cap) -> i32       bytes read (0 at end), or -1
//! ```
//!
//! Any other import is refused before the module runs. The declared `kind` (the protocol) is
//! recorded with the call and not enforced: the capability binds the target, not what is spoken
//! on it. CPU is bounded by fuel; each connect, send and receive by a timeout.

use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::{SocketAddr, TcpStream, ToSocketAddrs};
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Duration;

use anyhow::{Context as _, bail};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use topak_core::Digest;
use wasmtime::{Caller, Config, Engine, Linker, Module, Store};

/// A tool's declared effect channel (ADR-0040 §3; `mechanism/` I33's shape).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Channel {
    pub kind: String,
    /// `host:port`. The only address the module can reach.
    pub target: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WasmToolSpec {
    pub module: PathBuf,
    /// The module's bytes, pinned: the tool's allowlist digest.
    pub module_sha256: Digest,
    /// `None`: a hermetic tool (Build's P4), with no network at all.
    #[serde(default)]
    pub channel: Option<Channel>,
}

/// The capabilities the host grants, and nothing else.
const GRANTED: [&str; 6] = ["input_len", "input_read", "output", "connect", "send", "recv"];
const FUEL: u64 = 50_000_000;
const NET_TIMEOUT: Duration = Duration::from_secs(2);

struct Tool {
    spec: WasmToolSpec,
    module: Module,
}

pub struct WasmToolHost {
    engine: Engine,
    tools: BTreeMap<String, Tool>,
}

/// What one call did on its channel, for the record (ADR-0042 §3).
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ChannelUse {
    pub connects: u32,
    pub sent: u64,
    pub received: u64,
}

struct Ctx {
    input: Vec<u8>,
    output: Option<Vec<u8>>,
    channel: Option<Channel>,
    conns: Vec<TcpStream>,
    used: ChannelUse,
}

/// The allowlist digest of a module file: the SHA-256 of its bytes.
pub fn module_digest(path: &Path) -> anyhow::Result<Digest> {
    Ok(Digest::of(&std::fs::read(path)?))
}

/// Refuse a module that asks for anything the host does not grant. Linking would refuse it too;
/// this says why, before anything runs.
pub fn check_imports(module: &Module) -> anyhow::Result<()> {
    for imp in module.imports() {
        if imp.module() != "topak" || !GRANTED.contains(&imp.name()) {
            bail!(
                "import {}.{} is not a capability this tool host grants (ADR-0034 A2, P4: channel fidelity)",
                imp.module(),
                imp.name()
            );
        }
    }
    Ok(())
}

fn resolve(target: &str) -> anyhow::Result<SocketAddr> {
    target.to_socket_addrs()?.next().with_context(|| format!("{target} resolves to nothing"))
}

fn memory(caller: &mut Caller<'_, Ctx>) -> wasmtime::Result<wasmtime::Memory> {
    caller
        .get_export("memory")
        .and_then(|e| e.into_memory())
        .ok_or_else(|| wasmtime::Error::msg("the module exports no memory"))
}

/// Wasmtime's errors are its own; the host reports them as `anyhow`'s.
fn wt<T>(r: wasmtime::Result<T>) -> anyhow::Result<T> {
    r.map_err(|e| anyhow::anyhow!("{e:?}"))
}

impl WasmToolHost {
    /// Compile every module, after checking its bytes against the pin and its imports against
    /// the grant. A tool that fails either is not hosted, and the node refuses to start.
    pub fn new(specs: BTreeMap<String, WasmToolSpec>) -> anyhow::Result<Self> {
        let mut config = Config::new();
        config.consume_fuel(true);
        let engine = wt(Engine::new(&config))?;
        let mut tools = BTreeMap::new();
        for (id, spec) in specs {
            let bytes = std::fs::read(&spec.module).with_context(|| format!("tool {id}: {}", spec.module.display()))?;
            anyhow::ensure!(Digest::of(&bytes) == spec.module_sha256, "tool {id}: the module is not the pinned one");
            let module = wt(Module::new(&engine, &bytes)).with_context(|| format!("tool {id}"))?;
            check_imports(&module).with_context(|| format!("tool {id}"))?;
            tools.insert(id, Tool { spec, module });
        }
        Ok(WasmToolHost { engine, tools })
    }

    pub fn hosts(&self, id: &str) -> bool {
        self.tools.contains_key(id)
    }

    pub fn channel(&self, id: &str) -> Option<&Channel> {
        self.tools.get(id).and_then(|t| t.spec.channel.as_ref())
    }

    pub fn ids(&self) -> impl Iterator<Item = &String> {
        self.tools.keys()
    }

    /// One call: a fresh instance, the inputs as JSON, the result as JSON. Runs on a blocking
    /// thread; the network calls inside it block.
    pub async fn call(self: &Arc<Self>, id: &str, inputs: &Map<String, Value>) -> anyhow::Result<(Value, ChannelUse)> {
        let me = self.clone();
        let id = id.to_string();
        let input = serde_json::to_vec(inputs)?;
        tokio::task::spawn_blocking(move || me.call_blocking(&id, input)).await?
    }

    fn call_blocking(&self, id: &str, input: Vec<u8>) -> anyhow::Result<(Value, ChannelUse)> {
        let tool = self.tools.get(id).with_context(|| format!("tool {id} is not hosted"))?;
        let ctx =
            Ctx { input, output: None, channel: tool.spec.channel.clone(), conns: vec![], used: ChannelUse::default() };
        let mut store = Store::new(&self.engine, ctx);
        wt(store.set_fuel(FUEL))?;
        let mut linker: Linker<Ctx> = Linker::new(&self.engine);
        wt(linker.func_wrap("topak", "input_len", |c: Caller<'_, Ctx>| c.data().input.len() as i32))?;
        wt(linker.func_wrap("topak", "input_read", |mut c: Caller<'_, Ctx>, ptr: i32| -> wasmtime::Result<()> {
            let mem = memory(&mut c)?;
            let input = c.data().input.clone();
            mem.write(&mut c, ptr as usize, &input)?;
            Ok(())
        }))?;
        wt(linker.func_wrap(
            "topak",
            "output",
            |mut c: Caller<'_, Ctx>, ptr: i32, len: i32| -> wasmtime::Result<()> {
                let mem = memory(&mut c)?;
                let mut buf = vec![0u8; len.max(0) as usize];
                mem.read(&c, ptr as usize, &mut buf)?;
                c.data_mut().output = Some(buf);
                Ok(())
            },
        ))?;
        // The only network capability: the declared target. No address crosses this boundary.
        wt(linker.func_wrap("topak", "connect", |mut c: Caller<'_, Ctx>| -> i32 {
            let Some(ch) = c.data().channel.clone() else { return -1 };
            let Ok(addr) = resolve(&ch.target) else { return -1 };
            match TcpStream::connect_timeout(&addr, NET_TIMEOUT) {
                Ok(s) => {
                    let _ = s.set_read_timeout(Some(NET_TIMEOUT));
                    let _ = s.set_write_timeout(Some(NET_TIMEOUT));
                    let d = c.data_mut();
                    d.conns.push(s);
                    d.used.connects += 1;
                    (d.conns.len() - 1) as i32
                }
                Err(_) => -1,
            }
        }))?;
        wt(linker.func_wrap(
            "topak",
            "send",
            |mut c: Caller<'_, Ctx>, h: i32, ptr: i32, len: i32| -> wasmtime::Result<i32> {
                let mem = memory(&mut c)?;
                let mut buf = vec![0u8; len.max(0) as usize];
                mem.read(&c, ptr as usize, &mut buf)?;
                let d = c.data_mut();
                let Some(s) = d.conns.get_mut(h as usize) else { return Ok(-1) };
                Ok(match s.write_all(&buf) {
                    Ok(()) => {
                        d.used.sent += buf.len() as u64;
                        buf.len() as i32
                    }
                    Err(_) => -1,
                })
            },
        ))?;
        wt(linker.func_wrap(
            "topak",
            "recv",
            |mut c: Caller<'_, Ctx>, h: i32, ptr: i32, cap: i32| -> wasmtime::Result<i32> {
                let mut buf = vec![0u8; cap.max(0) as usize];
                let n = {
                    let d = c.data_mut();
                    let Some(s) = d.conns.get_mut(h as usize) else { return Ok(-1) };
                    match s.read(&mut buf) {
                        Ok(n) => n,
                        Err(_) => return Ok(-1),
                    }
                };
                c.data_mut().used.received += n as u64;
                let mem = memory(&mut c)?;
                mem.write(&mut c, ptr as usize, &buf[..n])?;
                Ok(n as i32)
            },
        ))?;
        let instance = wt(linker.instantiate(&mut store, &tool.module))?;
        let run = wt(instance.get_typed_func::<(), i32>(&mut store, "run"))?;
        let rc = wt(run.call(&mut store, ()))?;
        let used = store.data().used.clone();
        anyhow::ensure!(rc == 0, "the tool returned {rc}");
        let out = store.into_data().output.unwrap_or_default();
        let value = if out.is_empty() {
            Value::Null
        } else {
            serde_json::from_slice(&out).context("the tool's output is not JSON")?
        };
        Ok((value, used))
    }
}
