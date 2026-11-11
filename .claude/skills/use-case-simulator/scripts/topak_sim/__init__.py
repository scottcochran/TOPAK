"""A kernel for simulating TOPAK use cases and replaying what happened.

    trace     the hash-chained event format, and the only code that applies state changes
    policy    the real evaluators: bundles in opa-wasm, the linked Cedar floor, the workflow Run
    lift      the frozen input, built as mechanism/crates/topak-core/src/lift.rs builds it
    core      the recorder, the admission path, pins, scenarios and the tick loop
    workflow  a promoted DAG or mesh, driven through the reference's own Run
    overlay   an autonomous plane of the command-chain overlay (ADR-0059 to ADR-0068)
    replay    verification and inspection of a trace, with no simulator
"""
