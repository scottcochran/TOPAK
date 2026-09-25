//! Drift check (ADR-0033, open obligations).
//!
//! `mechanism/corpus-pins.sha256` records the digest of every record and TLA+ module the
//! reference follows, as the reference last followed it. A pin that no longer matches means the
//! corpus moved and the reference has not been reviewed against it: drift caught, not discovered.
//!
//! The pin is whole-file, so any edit trips it, including a History row or a pending amendment.
//! That is deliberate for a first cut. Re-pinning is the review's record: read the change, bring
//! the code into line or register why not in `GAPS-AND-ASSUMPTIONS.md`, then replace the line.
//!
//! A second test keeps the pin list honest: every record or module the reference's code cites
//! must be pinned, so citing a new one without pinning it fails too.

use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../..").canonicalize().expect("repository root")
}

fn mechanism_root() -> PathBuf {
    repo_root().join("mechanism")
}

/// `<sha256>  <path>` lines, paths relative to the repository root (`shasum -a 256 -c` format).
fn pins() -> BTreeMap<String, String> {
    let text = fs::read_to_string(mechanism_root().join("corpus-pins.sha256")).expect("corpus-pins.sha256");
    text.lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| {
            let (digest, path) = l.split_once("  ").unwrap_or_else(|| panic!("malformed pin line: {l}"));
            (path.trim().to_owned(), digest.trim().to_owned())
        })
        .collect()
}

#[test]
fn pinned_records_have_not_drifted() {
    let root = repo_root();
    let mut drifted = Vec::new();
    for (path, pinned) in pins() {
        let bytes = fs::read(root.join(&path)).unwrap_or_else(|e| panic!("pinned {path}: {e}"));
        let actual = hex::encode(Sha256::digest(&bytes));
        if actual != pinned {
            drifted.push(format!("  {path}\n    pinned {pinned}\n    actual {actual}"));
        }
    }
    assert!(
        drifted.is_empty(),
        "{} pinned file(s) changed since the reference last followed them:\n{}\n\n\
         Review each change against the reference. Bring the code into line, or register the divergence in \
         GAPS-AND-ASSUMPTIONS.md; then re-pin (`shasum -a 256 <path>` from the repository root).",
        drifted.len(),
        drifted.join("\n"),
    );
}

/// Source files whose citations count: code, manifests and scripts. The register and README cite
/// records for context, not because the reference implements them, so they are not scanned.
fn sources(dir: &Path, out: &mut Vec<PathBuf>) {
    for entry in fs::read_dir(dir).expect("read_dir").flatten() {
        let p = entry.path();
        if p.is_dir() {
            if p.file_name().is_some_and(|n| n != "target") {
                sources(&p, out);
            }
        } else if p.extension().is_some_and(|e| ["rs", "toml", "sh", "py"].iter().any(|x| e == *x)) {
            out.push(p);
        }
    }
}

/// `ADR-NNNN` → `decisions/ADR-NNNN.md`; `Name.tla` → `spec/Name.tla` when that module exists.
fn citations(text: &str, root: &Path) -> BTreeSet<String> {
    let mut found = BTreeSet::new();
    let b = text.as_bytes();
    for (i, _) in text.match_indices("ADR-") {
        let n = &b[i + 4..(i + 8).min(b.len())];
        if n.len() == 4 && n.iter().all(u8::is_ascii_digit) {
            found.insert(format!("decisions/ADR-{}.md", std::str::from_utf8(n).unwrap()));
        }
    }
    for (i, _) in text.match_indices(".tla") {
        let start = text[..i].rfind(|c: char| !(c.is_ascii_alphanumeric() || c == '_')).map_or(0, |s| s + 1);
        let module = format!("spec/{}.tla", &text[start..i]);
        if start < i && root.join(&module).is_file() {
            found.insert(module);
        }
    }
    found
}

#[test]
fn every_cited_record_is_pinned() {
    let root = repo_root();
    let mech = mechanism_root();
    let mut files = Vec::new();
    sources(&mech.join("crates"), &mut files);
    sources(&mech.join("scripts"), &mut files);

    let pinned = pins();
    let mut unpinned: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for f in &files {
        let text = fs::read_to_string(f).unwrap_or_default();
        for cited in citations(&text, &root) {
            if !pinned.contains_key(&cited) {
                let at = f.strip_prefix(&mech).unwrap_or(f).display().to_string();
                unpinned.entry(cited).or_default().insert(at);
            }
        }
    }
    assert!(
        unpinned.is_empty(),
        "cited by the reference but not pinned in corpus-pins.sha256:\n{}",
        unpinned
            .iter()
            .map(|(r, at)| format!("  {r}  (cited in {})", Vec::from_iter(at.iter().cloned()).join(", ")))
            .collect::<Vec<_>>()
            .join("\n"),
    );
}
