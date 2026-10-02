#!/bin/bash
# Regenerates the TLC evidence for ADR-0046 §5's corrections to theorem-premise-binding.md: the mutation rows
# the original results files did not run, and the unread bounds at K >= R, each with the outcome the correction
# predicts. Two control rows at the original constants show the backlog refusal reachable when K < R, which is
# why ADR-0039 §1 still requires it.
#   usage: premise-corrections-results.sh > premise-corrections-results-<date>.txt
# Exits non-zero if any row's outcome differs from the expected one.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
jar=${TLA_JAR:-$root/tools/tla2tools.jar}
export TLA_JAR=$jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
d() { shasum -a 256 "$here/$1" | cut -c1-16; }
echo "TOPAK — TLC rows for ADR-0046 §5: the premise-table corrections the proofs found, checked by model checking"
echo "Modules: FloorComposition.tla (sha256 $(d FloorComposition.tla)) · Coupling.tla (sha256 $(d Coupling.tla)) · RunCoupling.tla (sha256 $(d RunCoupling.tla))"
echo "TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1) · drivers: floor-run.sh, coupling-run.sh, runcoupling-run.sh"
echo "Corpus at $(cd "$root" && git rev-parse --short HEAD)$(cd "$root" && git diff --quiet HEAD -- spec/FloorComposition.tla spec/Coupling.tla spec/RunCoupling.tla || echo ' + working tree')"
echo "Each row: name | module or Mut | invariant | result | states | expected | verdict. A COUNTEREXAMPLE row is a mutation"
echo "breaking the invariant; a HOLDS row at K >= R is the bound holding without K < R; a Never… row at K >= R that"
echo "HOLDS is the backlog refusal unreachable, and its control at the original constants is a COUNTEREXAMPLE."
echo
status=0
row() { # expected, then the driver line
  exp=$1; shift
  line=$( (cd "$here" && "$@") | head -1)
  got=$(echo "$line" | awk -F' \\| ' '{for(i=1;i<=NF;i++) if($i=="HOLDS"||$i=="COUNTEREXAMPLE"||$i=="ERROR") print $i}')
  if [ "$got" = "$exp" ]; then v="AS EXPECTED"; else v="UNEXPECTED"; status=1; fi
  echo "$line | expected $exp | $v"
  name=$2; [ "$1" = "./floor-run.sh" ] && name=$3
  rm -rf "/tmp/tlc_$name"
}
echo "-- FloorComposition: mutations TLC did not run (correction 2 of ADR-0046 §5)"
row COUNTEREXAMPLE ./floor-run.sh FloorComposition pc-override-err    M_OVERRIDE FloorErrorIsDeny
row COUNTEREXAMPLE ./floor-run.sh FloorComposition pc-override-bundle M_OVERRIDE BundleRefusalHonored
row COUNTEREXAMPLE ./floor-run.sh FloorComposition pc-err-floor       M_ERR      AdmitImpliesFloorPermit
echo
echo "-- Coupling: UnreadBounded without K < R (the struck parameter premise), K R MaxRound as shown"
row HOLDS          ./coupling-run.sh pc-c-k3r2           none UnreadBounded       3 2 2
row HOLDS          ./coupling-run.sh pc-c-k5r2           none UnreadBounded       5 2 2
row HOLDS          ./coupling-run.sh pc-c-k3r2-backlog   none NeverBacklogRefusal 3 2 2
row COUNTEREXAMPLE ./coupling-run.sh pc-c-k1r3-backlog   none NeverBacklogRefusal 1 3 2
echo
echo "-- RunCoupling: UnreadEffectsBounded without K < R, K R MaxRound as shown"
row HOLDS          ./runcoupling-run.sh pc-rc-k3r2          none UnreadEffectsBounded   3 2 2
row HOLDS          ./runcoupling-run.sh pc-rc-k3r2-actuates none NeverRefusedOnActuates 3 2 2
row COUNTEREXAMPLE ./runcoupling-run.sh pc-rc-k1r4-actuates none NeverRefusedOnActuates 1 4 2
echo
echo "Not rerun here: RunSeats' correction (1) is in RunSeats-results-2026.09.29.txt (rs-obsemit-safe HOLDS,"
echo "rs-mdomain-observer COUNTEREXAMPLE); RunCoupling's (3) in RunCoupling-results-2026.09.29.txt (rc-emitseq-seal"
echo "COUNTEREXAMPLE, rc-rounds-seal HOLDS); Confinement's (4) is a statement about the proof (SameGuest appears only"
echo "in Confinement_proof.tla's M_UNBOUND lemma) and has no TLC row."
exit $status
