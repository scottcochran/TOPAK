#!/bin/bash
# Regenerates the Lean results file for the genesis floor under Cedar's verified semantics (ADR-0053, Proposed):
# regenerates TopakFloor/Genesis.lean and TopakFloor/Tests.lean from the floor's files (gen.py, through the cedar CLI),
# does a clean build of this package against cedar-spec's Lean model at the pinned commit, and prints the digests of
# the floor, the schema, the tests, the parser, the generated and hand-written Lean, the model and the toolchain, the
# `#print axioms` of every theorem, and the kernel replay. Regenerates byte for byte on the same machine.
#   usage: results.sh > TopakFloor-results-<date>.txt     (from floor/lean/; needs cedar on PATH, ~/.cargo/bin by
#   default, and network for lake's first fetch of cedar-spec and batteries)
# tools/lean-sync.sh says whether the newest results file still matches the tree and the pin.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
export PATH="$HOME/.cargo/bin:$PATH"
(cd "$here" && python3 gen.py >/dev/null) || { echo "gen.py failed" >&2; exit 2; }
rev() { python3 -c "import json,sys;m=json.load(open('$here/lake-manifest.json'));print(next(p['rev'] for p in m['packages'] if p['name']==sys.argv[1]))" "$1"; }
echo "TOPAK — Lean results for the genesis floor and the floor in force under Cedar's verified semantics: every theorem of floor/lean/TopakFloor/*.lean, checked by the kernel below"
echo "Floor: $(e floor/genesis-floor.cedar) · $(e floor/genesis.cedarschema) · $(e floor/genesis-tests.json) · in force: $(e floor/proposed/emergency-floor.cedar) · $(e floor/proposed/emergency.cedarschema) · $(e floor/proposed/emergency-tests.json)"
echo "Parser: $(cedar --version) (sha256 $(shasum -a 256 "$(command -v cedar)" | cut -c1-16)), translate-policy and translate-schema, walked by gen.py"
echo "Sources: $(e floor/lean/TopakFloor/Basic.lean) · $(e floor/lean/TopakFloor/Genesis.lean) · $(e floor/lean/TopakFloor/Tests.lean) · $(e floor/lean/TopakFloor/Gates.lean) · $(e floor/lean/TopakFloor/Emergency.lean) · $(e floor/lean/TopakFloor/EmergencyTests.lean) · $(e floor/lean/TopakFloor/InForce.lean) · $(e floor/lean/TopakFloor.lean) · $(e floor/lean/gen.py) · $(e floor/lean/lakefile.lean) · $(e floor/lean/lake-manifest.json) · $(e floor/lean/lean-toolchain)"
echo "Model: cedar-spec $(grep -oE '@ "v[0-9.]+"' "$here/lakefile.lean" | tr -d '@ "') (commit $(rev Cedar)), libraries Cedar.Spec, Cedar.Validation, Cedar.Thm.Validation · batteries (commit $(rev batteries)) · the mechanism links cedar-policy $(grep -A1 'name = "cedar-policy"$' "$root/mechanism/Cargo.lock" | sed -n 's/version = "\(.*\)"/\1/p')"
"$root/tools/lean-report.sh" "$here" --prover
echo "Theorems (Gates): $(grep -oE "^theorem [A-Za-z_][A-Za-z0-9_']* *[(:]" "$here/TopakFloor/Gates.lean" | sed -E 's/theorem //; s/ *[(:]$//' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (Tests): $(grep -c '^theorem case' "$here/TopakFloor/Tests.lean") cases of genesis-tests.json, each isAuthorized = the case's response"
echo "Theorems (InForce): $(grep -oE "^theorem [A-Za-z_][A-Za-z0-9_']* *[(:]" "$here/TopakFloor/InForce.lean" | sed -E 's/theorem //; s/ *[(:]$//' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (EmergencyTests): $(grep -c '^theorem emCase' "$here/TopakFloor/EmergencyTests.lean") cases of proposed/emergency-tests.json, the floor in force, each isAuthorized = the case's response"
echo "A theorem holds of the floor as gen.py states it in the model's syntax from the cedar CLI's parse, under the model's semantics; the model's fidelity to the engine is T-0045-3. Closed evaluations are by native_decide, one axiom per use in the axiom lines below; the kernel's decide cannot reduce the model's definitions. The solver-backed gates (routing, every-entry-matters) stay with run-gates.py and the checker."
echo
"$root/tools/lean-report.sh" "$here" TopakFloor
