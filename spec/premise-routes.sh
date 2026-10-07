#!/bin/bash
# Shows what the derived premises do to the inventory (ADR-0053 R7, merged into the binding at ratification, Batch
# 36): evaluates the binding for the reference's rows as ADR-0045 Annex B declares them and four variations, every
# premise column of kind parameter, condition or gap declared true so that only the rows and routes differ.
# premise-routes-results-2026.10.06.txt is the run before the merge, with the binding and the overlay apart.
#   usage: premise-routes.sh > premise-routes-results-<date>.txt     (from spec/)
# Byte for byte while the graph check's results stay in sync. Exits non-zero if the overlay is not well formed.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
tmp=$(mktemp -d /tmp/topak-routes.XXXXXX)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
echo "TOPAK — the premise table with derived premises (ADR-0053, Batch 36): which route carries each theorem, and what a deployment cannot lose"
echo "Sources: $(e spec/theorem-premise-binding.json) · $(e spec/theorem-premise-binding.md) · $(e spec/inventory.py) · $(e spec/premise-routes.sh) · $(e decisions/ADR-0045.md)"
echo "Each declaration: the reference's rows from ADR-0045 Annex B (inventory.py --annex-b), with the changes its heading names, and every premise column of kind parameter, condition or gap that is not an encoding's or a model's faithfulness declared true, so that a verdict differs only by its rows and routes. A check premise takes its value from its results file."
echo
python3 "$here/inventory.py" --check || exit 1
python3 - "$here" "$tmp" <<'PY'
import json, subprocess, sys
here, tmp = sys.argv[1], sys.argv[2]
ref = json.loads(subprocess.check_output(["python3", f"{here}/inventory.py", "--annex-b"]))
cols = json.load(open(f"{here}/theorem-premise-binding.json"))["premises"]
faith = lambda p: p.startswith("enc-faithful(") or p.startswith("model-faithful(")
base = {p: True for p, s in cols.items() if "derived" not in s and s.get("kind") != "check" and not faith(p)}
others = {p: True for p, s in cols.items() if s.get("kind") == "condition" and p.startswith("enc-faithful")}
def decl(name, rows=None, premises=None):
    d = {"rung": 0, "rows": dict(ref["rows"], **(rows or {})), "premises": dict(base, **(premises or {}))}
    json.dump(d, open(f"{tmp}/{name}.json", "w"), indent=1)
decl("1-reference")
decl("2-lean-not-tlaps", {"T-0045-31": "excluded", "T-0045-37": "trust root"})
decl("3-lean-every-encoding-read", {"T-0045-31": "excluded", "T-0045-37": "trust root"}, others)
decl("4-lean-stage-not-T28", {"T-0045-28": "excluded", "T-0045-37": "trust root"}, {"model-faithful(apply/Seats)": True})
decl("5-graph-check-refused", {"T-0045-31": "excluded", "T-0045-37": "trust root"},
     {"enc-faithful(Seats)": False, "enc-faithful(FloorComposition)": False})
PY
for d in 1-reference 2-lean-not-tlaps 3-lean-every-encoding-read 4-lean-stage-not-T28 5-graph-check-refused; do
  echo
  echo "=== $d"
  cuts=""; [ "$d" = 1-reference ] && cuts="--cuts"
  python3 "$here/inventory.py" "$tmp/$d.json" "$here/theorem-premise-binding.json" $cuts | sed "s|$here/||g; s|$tmp/||g"
done
rm -rf "$tmp"
