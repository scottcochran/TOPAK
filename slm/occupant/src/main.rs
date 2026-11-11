//! The trained SLM as a compiled occupant (ADR-0036 §3): a fixed Build round with the Persona inside.
//!
//!   occupant [round options]          the round, over the launcher's stdio (rung 1, the default)
//!   occupant --transport mcp …        the same round on the host, holding a token (rung 0)
//!   occupant generate …               host check: the continuation the round would draft
//!   occupant logits | encode | info   host checks for parity with slm/model.py
//!
//! The round: wait for the lease, `Read` each `--read` object, continue the text of what was read
//! with the Persona, `Draft` the continuation to `--target`, `Submit`. The alphabet is Read, Draft,
//! Submit; it never `Invoke`s (P4 vacuous). Stdout carries protocol lines only; everything else
//! goes to stderr, which the launcher logs and nobody reads back.
//!
//! The bundle is checked before the first line: a mismatch exits 3 with nothing written to stdout,
//! so a guest that cannot verify its bundle is never granted (ADR-0036 §2.1).

mod bundle;
mod channel;
mod model;
mod sample;

use std::path::PathBuf;
use std::process::exit;

use serde_json::{json, Value};

use bundle::Bundle;
use channel::{Channel, Op};
use sample::Opts;

/// Prompt text is capped before it is tokenized, as `serve.py`'s SLM_MAX_PROMPT_CHARS does.
const MAX_PROMPT_CHARS: usize = 16384;
const MAX_NEW: usize = 512;

fn usage(e: &str) -> ! {
    eprintln!("occupant: {e}");
    eprintln!(
        "usage: occupant [--bundle DIR] [--read DIGEST]... [--target PATH] [--max-new N] [--temperature T]\n\
         \x20               [--top-k K] [--seed S] [--hold-ms MS] [--transport stdio|mcp --topak BIN --socket PATH --token T]\n\
         \x20      occupant generate [--bundle DIR] (--prompt TEXT | --prompt-file PATH) [--max-new N] [--temperature T] [--top-k K] [--seed S]\n\
         \x20      occupant logits [--bundle DIR] --ids 1,2,3\n\
         \x20      occupant encode [--bundle DIR] (--prompt TEXT | --prompt-file PATH)\n\
         \x20      occupant info [--bundle DIR]"
    );
    exit(2)
}

#[derive(Default)]
struct Args {
    cmd: String,
    bundle: Option<PathBuf>,
    reads: Vec<String>,
    target: Option<String>,
    max_new: Option<usize>,
    temperature: Option<f32>,
    top_k: Option<usize>,
    seed: Option<u64>,
    hold_ms: u64,
    transport: Option<String>,
    topak: Option<String>,
    socket: Option<String>,
    token: Option<String>,
    prompt: Option<String>,
    prompt_file: Option<PathBuf>,
    ids: Option<String>,
}

fn parse() -> Args {
    let mut a = Args { cmd: "round".into(), ..Default::default() };
    let mut it = std::env::args().skip(1).peekable();
    if let Some(c) = it.peek() {
        if ["generate", "logits", "encode", "info"].contains(&c.as_str()) {
            a.cmd = it.next().unwrap();
        }
    }
    while let Some(flag) = it.next() {
        let mut val = || it.next().unwrap_or_else(|| usage(&format!("{flag} needs a value")));
        let num = |s: String, f: &str| s.parse::<u64>().unwrap_or_else(|_| usage(&format!("{f} must be a number")));
        match flag.as_str() {
            "--bundle" => a.bundle = Some(val().into()),
            "--read" => a.reads.push(val()),
            "--target" => a.target = Some(val()),
            "--max-new" => a.max_new = Some(num(val(), "--max-new") as usize),
            "--temperature" => {
                a.temperature = Some(val().parse().unwrap_or_else(|_| usage("--temperature must be a number")))
            }
            "--top-k" => a.top_k = Some(num(val(), "--top-k") as usize),
            "--seed" => a.seed = Some(num(val(), "--seed")),
            "--hold-ms" => a.hold_ms = num(val(), "--hold-ms"),
            "--transport" => a.transport = Some(val()),
            "--topak" => a.topak = Some(val()),
            "--socket" => a.socket = Some(val()),
            "--token" => a.token = Some(val()),
            "--prompt" => a.prompt = Some(val()),
            "--prompt-file" => a.prompt_file = Some(val().into()),
            "--ids" => a.ids = Some(val()),
            other => usage(&format!("unknown argument {other}")),
        }
    }
    a
}

fn opts(a: &Args) -> Opts {
    let o = Opts {
        max_new: a.max_new.unwrap_or(128),
        temperature: a.temperature.unwrap_or(0.0),
        top_k: a.top_k.unwrap_or(50),
        seed: a.seed.unwrap_or(0),
    };
    if !(1..=MAX_NEW).contains(&o.max_new) {
        usage(&format!("--max-new must be in [1, {MAX_NEW}]"));
    }
    if !(0.0..=2.0).contains(&o.temperature) {
        usage("--temperature must be in [0, 2]");
    }
    o
}

fn load(a: &Args) -> Bundle {
    let dir = a.bundle.clone().unwrap_or_else(|| PathBuf::from(std::env::var("SLM_BUNDLE").unwrap_or("/model".into())));
    bundle::load(&dir).unwrap_or_else(|e| {
        // ADR-0036 §2.1: no identity line from a guest that cannot verify its bundle.
        eprintln!("occupant: refused: {e}");
        exit(3)
    })
}

/// The last `MAX_PROMPT_CHARS` characters of `text`, encoded, keeping the last `ctx − max_new`
/// tokens so the window never slides during generation. Empty text starts a fresh document.
fn prompt_ids(b: &Bundle, text: &str, max_new: usize) -> Vec<u32> {
    let skip = text.chars().count().saturating_sub(MAX_PROMPT_CHARS);
    let tail: String = text.chars().skip(skip).collect();
    let mut ids = if tail.is_empty() {
        vec![]
    } else {
        b.tok.encode(tail.as_str(), true).expect("encodable").get_ids().to_vec()
    };
    if ids.is_empty() {
        ids = b.eot.into_iter().collect();
    }
    let keep = b.model.cfg.ctx.saturating_sub(max_new).max(1);
    if ids.len() > keep {
        ids.drain(..ids.len() - keep);
    }
    ids
}

/// What the round drafts for a given text: the Persona's continuation, decoded.
fn continuation(b: &Bundle, text: &str, o: &Opts) -> String {
    let ids = prompt_ids(b, text, o.max_new);
    let out = sample::generate(&b.model, &ids, o, b.eot);
    b.tok.decode(&out, true).expect("decodable")
}

fn read_prompt(a: &Args) -> String {
    match (&a.prompt, &a.prompt_file) {
        (Some(p), None) => p.clone(),
        (None, Some(f)) => std::fs::read_to_string(f).unwrap_or_else(|e| usage(&format!("{}: {e}", f.display()))),
        _ => usage("give one of --prompt or --prompt-file"),
    }
}

fn info(b: &Bundle) -> Value {
    json!({
        "model_json_sha256": b.persona,
        "weights_sha256": b.desc["weights"],
        "tokenizer_sha256": b.desc["tokenizer"],
        "family": b.desc["family_tag"],
        "params": b.desc["params"],
        "root": b.desc["root"],
        "ctx": b.model.cfg.ctx,
    })
}

fn round(a: &Args, b: &Bundle, ch: &mut dyn Channel) -> Result<(), String> {
    let o = opts(a);
    let mut text = String::new();
    for d in &a.reads {
        let r = ch.act(&Op::Read { object: d.clone() }).ok_or("the round ended during Read")?;
        if !r.admitted {
            return Err(format!("Read {} refused: {}", &d[..d.len().min(16)], r.detail));
        }
        let content = r.detail["result"]["content"].as_str().ok_or_else(|| format!("Read returned no content: {}", r.detail))?;
        eprintln!("occupant: read {} ({} bytes)", &d[..d.len().min(16)], content.len());
        text.push_str(content);
    }
    let t0 = std::time::Instant::now();
    let drafted = continuation(b, &text, &o);
    eprintln!("occupant: the Persona drafted {} bytes in {} ms", drafted.len(), t0.elapsed().as_millis());
    let target = a.target.clone().unwrap_or("notes.md".into());
    let r = ch.act(&Op::Draft { target: target.clone(), content: drafted }).ok_or("the round ended during Draft")?;
    if !r.admitted {
        return Err(format!("Draft {target} refused: {}", r.detail));
    }
    eprintln!("occupant: drafted {target}: {}", r.detail);
    if a.hold_ms > 0 {
        eprintln!("occupant: holding {} ms before Submit", a.hold_ms);
        std::thread::sleep(std::time::Duration::from_millis(a.hold_ms));
    }
    let r = ch.act(&Op::Submit).ok_or("the round ended during Submit")?;
    if !r.admitted {
        return Err(format!("Submit refused: {}", r.detail));
    }
    eprintln!("occupant: submitted: {}", r.detail);
    Ok(())
}

fn main() {
    let a = parse();
    match a.cmd.as_str() {
        "info" => println!("{}", info(&load(&a))),
        "encode" => {
            let b = load(&a);
            let ids = b.tok.encode(read_prompt(&a).as_str(), true).expect("encodable").get_ids().to_vec();
            println!("{}", json!({ "ids": ids }));
        }
        "logits" => {
            let b = load(&a);
            let ids: Vec<u32> = a.ids.as_deref().unwrap_or_else(|| usage("--ids is required")).split(',')
                .map(|s| s.trim().parse().unwrap_or_else(|_| usage("--ids is comma-separated token ids")))
                .collect();
            if ids.is_empty() || ids.len() > b.model.cfg.ctx || ids.iter().any(|&i| i as usize >= b.model.cfg.vocab) {
                usage("--ids must be 1..ctx ids within the vocabulary");
            }
            let mut c = b.model.cache();
            println!("{}", json!({ "logits": b.model.forward(&mut c, &ids) }));
        }
        "generate" => {
            let b = load(&a);
            let o = opts(&a);
            let text = read_prompt(&a);
            let ids = prompt_ids(&b, &text, o.max_new);
            let out = sample::generate(&b.model, &ids, &o, b.eot);
            let decoded = b.tok.decode(&out, true).expect("decodable");
            println!("{}", json!({ "prompt_ids": ids, "ids": out, "text": decoded }));
        }
        _ => {
            let b = load(&a);
            let i = info(&b);
            match a.transport.as_deref().unwrap_or("stdio") {
                "stdio" => {
                    let stdin = std::io::stdin();
                    let mut ch = channel::Stdio::new(stdin.lock(), std::io::stdout());
                    let family = b.desc["family_tag"].as_str().unwrap_or("").to_string();
                    let params = b.desc["params"]["total"].as_u64().unwrap_or(0);
                    ch.hello(&b.persona, &family, params, i["root"].as_str().unwrap_or(""));
                    if !ch.wait_for_lease() {
                        eprintln!("occupant: shut down before a lease");
                        return;
                    }
                    if let Err(e) = round(&a, &b, &mut ch) {
                        eprintln!("occupant: {e}");
                    }
                    ch.drain();
                }
                "mcp" => {
                    let need = |v: &Option<String>, f: &str| v.clone().unwrap_or_else(|| usage(&format!("--transport mcp needs {f}")));
                    let mut ch = channel::Mcp::start(&need(&a.topak, "--topak"), &need(&a.socket, "--socket"), &need(&a.token, "--token"))
                        .unwrap_or_else(|e| {
                            eprintln!("occupant: {e}");
                            exit(4)
                        });
                    let r = round(&a, &b, &mut ch);
                    ch.close();
                    if let Err(e) = r {
                        eprintln!("occupant: {e}");
                        exit(1);
                    }
                }
                other => usage(&format!("unknown transport {other}")),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::channel::{read_line, report_data, Channel, Op, Stdio, MAX_LINE};
    use std::io::Cursor;

    #[test]
    fn report_data_is_the_canonical_digest() {
        // python3 -c 'import hashlib,json;print(hashlib.sha256(json.dumps({"nonce":"ab","sessionKey":None},
        //   sort_keys=True,separators=(",",":")).encode()).hexdigest())'
        assert_eq!(report_data("ab"), "b9c0e6bd74a419044daabf3c66e36a97400e8e8e89fc8b69c279a31ceccaff12");
        let s = serde_json::json!({ "nonce": "ab", "sessionKey": null }).to_string();
        assert_eq!(s, r#"{"nonce":"ab","sessionKey":null}"#);
    }

    #[test]
    fn the_guest_answers_attest_waits_for_the_lease_and_reads_responses() {
        let host = concat!(
            r#"{"msg":"attest","nonce":"00"}"#, "\n",
            r#"{"msg":"granted","fence":7,"epoch":0}"#, "\n",
            r#"{"msg":"attest","nonce":"01"}"#, "\n",
            r#"{"msg":"granted","fence":7,"epoch":0}"#, "\n",
            r#"{"msg":"response","response":{"admitted":true,"detail":{"result":{"content":"hi"}}}}"#, "\n",
            r#"{"msg":"shutdown"}"#, "\n",
        );
        let mut out = Vec::new();
        {
            let mut ch = Stdio::new(Cursor::new(host.as_bytes()), &mut out);
            ch.hello("p", "decoder-transformer", 1, "r");
            assert!(ch.wait_for_lease());
            let r = ch.act(&Op::Read { object: "d".into() }).unwrap();
            assert!(r.admitted);
            assert_eq!(r.detail["result"]["content"], "hi");
            assert!(ch.act(&Op::Submit).is_none(), "shutdown ends the round");
        }
        let lines: Vec<serde_json::Value> =
            String::from_utf8(out).unwrap().lines().map(|l| serde_json::from_str(l).unwrap()).collect();
        let kinds: Vec<&str> = lines.iter().map(|l| l["msg"].as_str().unwrap()).collect();
        // The Read goes out after the lease; the renewal's attest is answered while waiting for its response.
        assert_eq!(kinds, ["hello", "evidence", "op", "evidence", "op"]);
        assert_eq!(lines[0]["session_key"], serde_json::Value::Null);
        assert_eq!(lines[1]["report_data"], report_data("00"));
        assert_eq!(lines[2]["op"]["action"]["kind"], "Read");
        assert_eq!(lines[2]["proof"], serde_json::Value::Null);
        assert_eq!(lines[3]["report_data"], report_data("01"));
        assert_eq!(lines[4]["op"]["op"], "submit_workspace");
    }

    #[test]
    fn lines_are_bounded() {
        let long = "x".repeat(MAX_LINE + 2) + "\n";
        assert!(read_line(&mut Cursor::new(long.as_bytes())).is_err());
        let ok = "x".repeat(MAX_LINE) + "\n";
        assert_eq!(read_line(&mut Cursor::new(ok.as_bytes())).unwrap().unwrap().len(), MAX_LINE);
    }
}
