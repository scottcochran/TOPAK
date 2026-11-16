//! ADR-0036 §2.1: a guest that cannot verify its bundle exits before its identity line. The
//! occupant exits 3 and writes nothing to stdout, so the launcher sees the channel close and
//! grants nothing.

use std::process::{Command, Stdio};

fn bundle(name: &str, weights: &[u8], recorded: &[u8]) -> std::path::PathBuf {
    let d = std::env::temp_dir().join(format!("occupant-refusal-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    std::fs::create_dir_all(&d).unwrap();
    let hex = |b: &[u8]| {
        use std::fmt::Write;
        let h = <sha2::Sha256 as sha2::Digest>::digest(b);
        h.iter().fold(String::new(), |mut s, x| {
            let _ = write!(s, "{x:02x}");
            s
        })
    };
    std::fs::write(d.join("model.safetensors"), weights).unwrap();
    std::fs::write(d.join("tokenizer.json"), b"{}").unwrap();
    let model = serde_json::json!({ "weights": hex(recorded), "tokenizer": hex(b"{}"), "model_config": {} });
    std::fs::write(d.join("model.json"), serde_json::to_vec(&model).unwrap()).unwrap();
    d
}

fn run(dir: &std::path::Path) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_occupant"))
        .args(["--bundle", dir.to_str().unwrap()])
        .stdin(Stdio::null())
        .output()
        .unwrap()
}

#[test]
fn weights_that_do_not_match_model_json_exit_3_with_nothing_on_stdout() {
    let d = bundle("weights", b"swapped weights", b"the weights model.json names");
    let out = run(&d);
    assert_eq!(out.status.code(), Some(3));
    assert!(out.stdout.is_empty(), "no identity line: {:?}", String::from_utf8_lossy(&out.stdout));
    assert!(String::from_utf8_lossy(&out.stderr).contains("model.safetensors digest"));
}

#[test]
fn a_missing_bundle_exits_3_with_nothing_on_stdout() {
    let out = run(std::path::Path::new("/nonexistent/bundle"));
    assert_eq!(out.status.code(), Some(3));
    assert!(out.stdout.is_empty());
}
