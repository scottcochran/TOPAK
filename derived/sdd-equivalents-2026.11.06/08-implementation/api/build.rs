// Layer: implementation · API specification, spec-as-source · TOPAK source: ../06-interface/api/lease.proto
// With protobuf the implementation-layer artifact is the generator invocation: tonic-build turns the
// .proto into Rust types and a service trait, and nobody edits the output. The edge from
// `generated/topak.lease.v1.rs` to `lease.proto` is *generated* (ADR-0057 §3): what it leaves to a
// person is the generator, prost/tonic, pinned in Cargo.lock. The hand-written part is the trait impl.
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .out_dir("generated")                  // checked in so the digest is reviewable; regenerated, never edited
        .compile_protos(&["../../06-interface/api/lease.proto"], &["../../06-interface/api"])?;
    println!("cargo:rerun-if-changed=../../06-interface/api/lease.proto");
    Ok(())
}
