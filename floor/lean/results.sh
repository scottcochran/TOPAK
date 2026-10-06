#!/bin/bash
# Regenerates the Lean results file for the genesis floor under Cedar's verified semantics: regenerates
# TopakFloor/Genesis.lean and TopakFloor/Tests.lean from the floor's files (gen.py, through the cedar CLI), does a
# clean build of this package against cedar-spec's Lean model at the pinned tag, and prints the digests of the floor,
# the schema, the tests, the generated and hand-written Lean, the model's commit and the toolchain, and what each
# theorem rests on (`#print axioms`).
#   usage: results.sh > TopakFloor-results-<date>.txt     (from floor/lean/; needs cedar on PATH and network for the
#   first fetch of cedar-spec)
set -u
here=$(cd "$(dirname "$0")" && pwd)
floor=$(cd "$here/.." && pwd)
d16() { shasum -a 256 "$1" | cut -c1-16; }
export PATH="$HOME/.cargo/bin:$PATH"
(cd "$here" && python3 gen.py >/dev/null) || { echo "gen.py failed" >&2; exit 2; }
echo "TOPAK — Lean results for the genesis floor under Cedar's verified semantics: every theorem of floor/lean/TopakFloor/*.lean, checked by the kernel below"
echo "Floor: genesis-floor.cedar (sha256 $(d16 "$floor/genesis-floor.cedar")) · schema genesis.cedarschema (sha256 $(d16 "$floor/genesis.cedarschema")) · tests genesis-tests.json (sha256 $(d16 "$floor/genesis-tests.json")) · parsed by $(cedar --version)"
echo "Sources: Basic.lean (sha256 $(d16 "$here/TopakFloor/Basic.lean")) · Genesis.lean (sha256 $(d16 "$here/TopakFloor/Genesis.lean"), generated) · Tests.lean (sha256 $(d16 "$here/TopakFloor/Tests.lean"), generated) · Gates.lean (sha256 $(d16 "$here/TopakFloor/Gates.lean")) · gen.py (sha256 $(d16 "$here/gen.py")) · lakefile.lean (sha256 $(d16 "$here/lakefile.lean"))"
cedar_rev=$(cd "$here" && python3 -c "import json;m=json.load(open('lake-manifest.json'));print(next(p['rev'] for p in m['packages'] if p['name']=='Cedar'))" 2>/dev/null)
cedar_tag=$(grep -oE '@ "v[0-9.]+"' "$here/lakefile.lean" | tr -d '@ "')
echo "Model: cedar-spec $cedar_tag (commit ${cedar_rev:-unknown}), cedar-lean libraries Cedar.Spec, Cedar.Validation, Cedar.Thm.Validation · the mechanism links cedar-policy $(grep -A1 'name = "cedar-policy"$' "$floor/../mechanism/Cargo.lock" | sed -n 's/version = "\(.*\)"/\1/p')"
echo "Prover: $(cd "$here" && lean --version) · $(cd "$here" && lake --version | head -1) · toolchain $(cat "$here/lean-toolchain") · driver: results.sh"
echo "Theorems (Gates): $(grep -oE "^theorem [A-Za-z_][A-Za-z0-9_']* *[(:]" "$here/TopakFloor/Gates.lean" | sed -E 's/theorem //; s/ *[(:]$//' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (Tests): $(grep -c '^theorem case' "$here/TopakFloor/Tests.lean") cases of genesis-tests.json, each isAuthorized = the case's response"
echo "A theorem holds of the floor as gen.py states it in the model's syntax from the cedar CLI's parse, under the model's semantics; the model's fidelity to the engine is cedar-spec's claim. Closed evaluations are by native_decide, one axiom per use in the #print axioms lines below; the kernel's decide cannot reduce the model's definitions. The solver-backed gates (routing, every-entry-matters) stay with run-gates.py and the checker."
echo
(cd "$here" && rm -rf .lake/build && lake build 2>&1 | grep -vE '^\s*$|^trace:')
status=${PIPESTATUS[0]}
exit $status
