#!/bin/bash
# Regenerates a TLAPS proof results file: checks one proof module with the TLA+ Proof System and prints
# the results file with the digests of every local module in its EXTENDS chain and of the prover.
#   usage: proof-results.sh <Module>_proof > <Module>-proof-results-<date>.txt
# What each theorem claims, its hypotheses, and what stays with TLC are in the proof module's header.
# Needs the prover under tools/ (tools/install-tlaps.sh); exits non-zero if any obligation fails.
set -u
mod=${1:?usage: proof-results.sh <Module>_proof}
mod=${mod%.tla}
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
tlapm="$root/tools/tlapm"
[ -f "$here/$mod.tla" ] || { echo "no $here/$mod.tla" >&2; exit 2; }
cfg=$("$tlapm" --config 2>/dev/null)
bin=$(echo "$cfg" | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
ver() { echo "$cfg" | sed -n "s/^$1 version == \"\(.*\)\"$/\1/p" | head -1; }
# Every local module the proof module reaches through EXTENDS, in dependency order.
chain=""
visit() {
  local m=$1 d
  case " $chain " in *" $m "*) return ;; esac
  for d in $(grep -m1 '^EXTENDS' "$here/$m.tla" | sed 's/^EXTENDS//; s/,/ /g'); do
    [ -f "$here/$d.tla" ] && visit "$d"
  done
  chain="$chain $m"
}
visit "$mod"
digests=""
for m in $chain; do digests="$digests · $m.tla (sha256 $(shasum -a 256 "$here/$m.tla" | cut -c1-16))"; done
cache=$(mktemp -d /tmp/tlapm_proof.XXXXXX)
echo "TOPAK — TLAPS proof results for ${mod%_proof}.tla: every obligation of $mod.tla, checked by the prover below"
echo "Modules:${digests# ·}"
echo "Prover: tlapm $("$tlapm" --version) (binary sha256 $(shasum -a 256 "$bin" | cut -c1-16)) · backends: $(ver SMT) · $(ver zenon) · $(ver Isabelle) · LS4 for PTL · driver: proof-results.sh"
assumptions=$(grep -E '^ASSUME' "$here/$mod.tla" | sed 's/^ASSUME *//; s/  */ /g' | paste -sd '|' - | sed 's/|/ · /g')
echo "Assumptions: ${assumptions:-none}"
echo "Theorems: $(grep -oE '^THEOREM [A-Za-z0-9_]+' "$here/$mod.tla" | sed 's/THEOREM //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Lemmas: $(grep -oE '^LEMMA [A-Za-z0-9_]+' "$here/$mod.tla" | sed 's/LEMMA //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "A proved obligation is a theorem of the module under its assumptions and the hypotheses the statement names; the prover, not the constants, bounds the claim. Mutations and witnesses are behaviours and stay with TLC."
echo
(cd "$here" && "$tlapm" --cleanfp --strict --cache-dir "$cache" "$mod.tla" 2>&1 | grep -vE '^\(\* ')
status=${PIPESTATUS[0]}
rm -rf "$cache"
exit $status
