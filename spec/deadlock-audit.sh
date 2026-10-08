#!/bin/bash
# Audits -deadlock, the flag with which the run scripts below turn off TLC's report of a state that has no successor
# (a terminal state). For each module they run, at the constants their results files use and with no mutation, it
# asks TLC whether any reachable state is terminal and, if one is, whether every one is at the module's own end: the
# bound the row states.
#   usage: deadlock-audit.sh > deadlock-audit-results-<date>.txt      (from spec/)
# For each row it writes, in a mktemp directory, a wrapper module <Module>_DL that EXTENDS the module and adds only
# definitions, so the state graph is the module's own:
#   Terminal        == ~ENABLED <next>      (next: the next-state relation of the row's specification)
#   NotTerminal     == ~Terminal
#   AtBound         == <the row's bound>    (FALSE where the row states none: no terminal state is expected)
#   TerminalAtBound == Terminal => AtBound
# copies the module and the local modules it EXTENDS beside it, and runs TLC with INVARIANT NotTerminal and, where
# that is violated, INVARIANT TerminalAtBound. TLC checks an invariant in every state it reaches, the first time it
# reaches it, so these runs pass -deadlock themselves: the invariant, not TLC's check, is what reports a terminal
# state. A row whose TerminalAtBound is violated is rerun on one worker, so that the first terminal state not at the
# bound is the same on every run, and once with no invariant, for the size of the whole graph.
# The rows are unmutated. No run script builds a module of its own: each writes a .cfg and runs the module file, so
# a wrapper that EXTENDS the module sees the run's graph. The one construction is the <Module>Dump.tla that
# lean/graph-check.sh and lean/graph-check-emergency.sh write, which adds a variable holding the properties' values;
# the Dump rows rebuild it as those scripts do, Emergency_live's with its two properties over ENABLED among the
# values the variable holds.
# After the rows: the scripts that pass -deadlock, each with the rows that cover it, and the two that are not
# model-checking runs of a transition system, with the reason the flag is there or is not needed.
# Exits 1 if a stray deadlock is found, 2 if a row could not be checked (ERROR), else 0.
# ONLY=<extended regex> runs only the rows whose module matches it, and the header says so. WORKERS sets TLC's -workers
# (default auto). Every run's wrapper, .cfg, metadir, output and java.io.tmpdir are in the mktemp directory, which is
# removed at the end; nothing is written to spec/.
set -u
here=$(cd "$(dirname "$0")" && pwd)
cd "$here" || exit 2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
jar=$(cd "$(dirname "$jar")" && pwd)/$(basename "$jar")
workers=${WORKERS:-auto}

# Module | instance | constants | next | AtBound
#   instance: "EXTENDS <Spec>", the wrapper EXTENDS the module and TLC runs <Spec>, whose relation is next; or
#             "Dump <script> <properties>", the <Module>Dump.tla that <script> writes, with those properties, whose
#             relation DNext is next /\ props' = Props', and which TLC runs as DSpec.
#   constants: the .cfg's assignments, separated by ";". AtBound: TLA+ over the module's names; empty is FALSE.
rows() {
cat <<'ROWS'
# RulesFloorNV-run.sh: the three _full rows of RulesFloorNV-results-2026.09.15.txt. The file does not record Active;
# these sets give its counts (554, 554, 1074), and rev4's is ADR-0026 §6's floor for rev4, R1 to R3, R5 and R7. The
# bound: the one havoc issuance spent, or moot once promoted (Issue needs ~issued /\ ~promoted), and the one round
# closed: promoted, or every seat on the issued roster has voted or timed out.
RulesFloorNV | EXTENDS Spec | Humans = {h1, h2, h3, h4}; Author = h1; AnchorKeys = {h4}; Active = {"R1","R2","R3","R4","R5","R7"}; Mech = "param"; h1 = h1; h2 = h2; h3 = h3; h4 = h4 | Next | (issued \/ promoted) /\ (promoted \/ \A h \in rules.grant : votes[h] # "none" \/ h \in timedOut)
RulesFloorNV | EXTENDS Spec | Humans = {h1, h2, h3, h4}; Author = h1; AnchorKeys = {h4}; Active = {"R1","R2","R3","R4","R5","R7"}; Mech = "as0024"; h1 = h1; h2 = h2; h3 = h3; h4 = h4 | Next | (issued \/ promoted) /\ (promoted \/ \A h \in rules.grant : votes[h] # "none" \/ h \in timedOut)
RulesFloorNV | EXTENDS Spec | Humans = {h1, h2, h3, h4}; Author = h1; AnchorKeys = {h4}; Active = {"R1","R2","R3","R5","R7"}; Mech = "rev4"; h1 = h1; h2 = h2; h3 = h3; h4 = h4 | Next | (issued \/ promoted) /\ (promoted \/ \A h \in rules.grant : votes[h] # "none" \/ h \in timedOut)
# RulesFloorNV_rev5-run.sh: the base row. The same bound, with one vote per counted seat and no Timeout.
RulesFloorNV_rev5 | EXTENDS Spec | Active = {"R1","R2","R5","R7","R9"}; Mech = "rev5" | Next | (issued \/ promoted) /\ (promoted \/ \A h \in Counted : votes[h] # "none")
# NonComposition-run.sh. The bound: both effects admitted, the one break-glass invocation made (nothing resets
# bgActive), and every payload erased (under none a payload is the only class the erasure envelope admits).
NonComposition | EXTENDS Spec | Mut = "none" | Next | admitted = Effects /\ bgActive /\ \A e \in Effects : PayRec(e) \notin retained
# bootstrap-run.sh: anchor-base and bg-base. The bound: the epoch bound (Issue needs epoch < MaxEpoch).
Anchor | EXTENDS Spec | Active = {"R1","R2","R5","R6","R7","R9"}; Mut = "none"; MaxEpoch = 2 | Next | epoch = MaxEpoch
BreakGlass | EXTENDS Spec | Active = {"R1","R2","R5","R6","R7","R9"}; Mut = "none"; MaxEpoch = 2 | Next | epoch = MaxEpoch
# lease-run.sh and Lease_A1-run.sh: every row of their results files. The bound: the fleet-fence bound (Revoke needs
# epoch < MaxEpoch) and every principal revoked (RevokeLease(p) needs p \notin revoked, and R3 bars a revoked
# principal from every later grant).
Lease | EXTENDS Spec | Mut = "none"; MaxEpoch = 2; MaxFence = 3 | Next | epoch = MaxEpoch /\ revoked = Principals
Lease_A1 | EXTENDS Spec | Mut = "none"; MaxEpoch = 2; MaxFence = 3 | Next | epoch = MaxEpoch /\ revoked = Principals
# floor-run.sh, and premise-corrections-results.sh through it. No end is expected: Decide (FloorComposition) and
# Promote of the deployed set (FloorRouting) are always enabled.
FloorComposition | EXTENDS Spec | Mut = "none" | Next |
FloorRouting | EXTENDS Spec | Mut = "none" | Next |
# confinement-run.sh and confinement-gen-results.sh, with MODULE unset and MODULE=Confinement_A1: the safe0 to safe3
# rows. The bound: MaxGen launches used by every principal, and the fence bound or the log bound reached, bounds that
# only cut the state space (proof-method.md §1). At Declared = 3 VerifierFlip keeps Next enabled.
Confinement | EXTENDS Spec | Mut = "none"; Declared = 0; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement | EXTENDS Spec | Mut = "none"; Declared = 1; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement | EXTENDS Spec | Mut = "none"; Declared = 2; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement | EXTENDS Spec | Mut = "none"; Declared = 3; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement_A1 | EXTENDS Spec | Mut = "none"; Declared = 0; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement_A1 | EXTENDS Spec | Mut = "none"; Declared = 1; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement_A1 | EXTENDS Spec | Mut = "none"; Declared = 2; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
Confinement_A1 | EXTENDS Spec | Mut = "none"; Declared = 3; MaxEpoch = 1; MaxIdx = 4; MaxGen = 2 | Next | (\A p \in Principals : gens[p] = MaxGen) /\ (epoch = MaxEpoch \/ idx = MaxIdx)
# seats-run.sh, observers-run.sh. No end is expected: Grant or EndRound (Seats); EndRound(t), which has no guard.
Seats | EXTENDS Spec | Mut = "none" | Next |
Observers | EXTENDS Spec | Mut = "none" | Next |
# coupling-run.sh at its defaults, and at the two constants premise-corrections-results.sh gives it. No end is
# expected at any constants: CorrBeat has no guard.
Coupling | EXTENDS Spec | Mut = "none"; K = 1; R = 3; MaxRound = 2 | Next |
Coupling | EXTENDS Spec | Mut = "none"; K = 3; R = 2; MaxRound = 2 | Next |
Coupling | EXTENDS Spec | Mut = "none"; K = 5; R = 2; MaxRound = 2 | Next |
# runcoupling-run.sh at its defaults and at premise-corrections-results.sh's. No end is expected: one of GrantO and
# EndO is always enabled.
RunCoupling | EXTENDS Spec | Mut = "none"; K = 1; R = 4; MaxRound = 2 | Next |
RunCoupling | EXTENDS Spec | Mut = "none"; K = 3; R = 2; MaxRound = 2 | Next |
# runseats-run.sh; runconfinement-run.sh and runconfinement-gen-results.sh. No end is expected: each seat or
# principal is live, with EndRound enabled, or not, with Grant enabled.
RunSeats | EXTENDS Spec | Mut = "none" | Next |
RunConfinement | EXTENDS Spec | Mut = "none"; Filtered = FALSE | Next |
RunConfinement | EXTENDS Spec | Mut = "none"; Filtered = TRUE | Next |
# emergency-run.sh and emergency-gen-results.sh. No end is expected: ObsToggle has no guard.
Emergency | EXTENDS Spec | Mut = "none"; MaxRound = 2 | Next |
# a1-run.sh with BreakGlass_A1-rows.txt: a1-base, and a1-nor7, the row at which the property holds without R7. The
# bound: the epoch bound and the round bound (ADR-0052 §3: a round's lease has no successor).
BreakGlass_A1 | EXTENDS Spec | Mut = "none"; MaxRound = 2; MaxEpoch = 2; Active = {"R1","R2","R5","R6","R7","R9"} | Next | epoch = MaxEpoch /\ round = MaxRound
BreakGlass_A1 | EXTENDS Spec | Mut = "none"; MaxRound = 2; MaxEpoch = 2; Active = {"R1","R2","R5","R6","R9"} | Next | epoch = MaxEpoch /\ round = MaxRound
# a1-run.sh with NonComposition_A1-rows.txt. The bound: the round bound (Activate needs last < MaxRound), both
# effects admitted, every payload erased.
NonComposition_A1 | EXTENDS Spec | Mut = "none"; MaxRound = 2 | Next | last = MaxRound /\ admitted = Effects /\ \A e \in Effects : PayRec(e) \notin retained
# toollist-run.sh and toollist-gen-results.sh. No end is expected: Promote(r) of the revision that is not latest.
ToolList | EXTENDS Spec | Mut = "none" | Next |
# operators-run.sh and operators-gen-results.sh, at Ops = {a, b}. No end is expected: one of Vouch(o) and
# Unvouch(o) is enabled for each operator. Ops = {a, b, c} is not run (see the note after the rows).
Operators | EXTENDS Spec | Mut = "none"; Ops = {"a", "b"}; MaxRound = 2 | Next |
# correlator-run.sh and correlator-gen-results.sh: the defaults (19 of the 22 rows), Stores = {a, b} (none-safe2,
# oh-carried2), and MaxSends = MMiss = 2 (w-named2). The bound: every Thinker at the round bound, and the send bound.
Correlator | EXTENDS Spec | Mut = "none"; Thinkers = {"t1", "t2"}; Stores = {"a"}; Corrs = {"c1", "c2"}; Honest = {"c1"}; MaxRound = 2; MaxSends = 1; MMiss = 1 | Next | (\A t \in Thinkers : round[t] = MaxRound) /\ Cardinality(sends) = MaxSends
Correlator | EXTENDS Spec | Mut = "none"; Thinkers = {"t1", "t2"}; Stores = {"a", "b"}; Corrs = {"c1", "c2"}; Honest = {"c1"}; MaxRound = 2; MaxSends = 1; MMiss = 1 | Next | (\A t \in Thinkers : round[t] = MaxRound) /\ Cardinality(sends) = MaxSends
Correlator | EXTENDS Spec | Mut = "none"; Thinkers = {"t1", "t2"}; Stores = {"a"}; Corrs = {"c1", "c2"}; Honest = {"c1"}; MaxRound = 2; MaxSends = 2; MMiss = 2 | Next | (\A t \in Thinkers : round[t] = MaxRound) /\ Cardinality(sends) = MaxSends
# labels-run.sh and labels-gen-results.sh. The bound: the result sequence at MaxSeq ("results are 1..MaxSeq").
Labels | EXTENDS Spec | Mut = "none"; MaxSeq = 3 | Next | seq = MaxSeq
# live-gen-results.sh, at every set of constants its two row files use. SpecL is the specification without fairness;
# the fairness specifications are SpecL with fairness conjoined, and reach the same states by the same steps.
Coupling_live | EXTENDS SpecL | Mut = "none"; K = 1; R = 3; MaxRound = 2 | NextL |
Coupling_live | EXTENDS SpecL | Mut = "none"; K = 0; R = 3; MaxRound = 2 | NextL |
Coupling_live | EXTENDS SpecL | Mut = "none"; K = 2; R = 4; MaxRound = 3 | NextL |
Emergency_live | EXTENDS SpecL | Mut = "none"; MaxRound = 2 | NextL |
Emergency_live | EXTENDS SpecL | Mut = "none"; MaxRound = 3 | NextL |
# lean/graph-check.sh: its two unmutated rows, through the Dump module it writes.
Seats | Dump lean/graph-check.sh OnlyThinkersAuthor OneSeatPerPrincipal | Mut = "none" | Next |
FloorComposition | Dump lean/graph-check.sh AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds | Mut = "none" | Next |
# lean/graph-check-emergency.sh: its two unmutated rows, through the Dump module it writes. Both are at MaxRound = 2,
# and Emergency_live's Dump is over NextL, the relation of its SpecL.
Emergency | Dump lean/graph-check-emergency.sh EmergencyLeaseHasARosterQuorum EmergencyLeaseIsOneRound NoAgentHoldsAnEmergencySeat CallsAreAllowlisted ThinkerStillCoupled ActivationIsForensic | Mut = "none"; MaxRound = 2 | Next |
Emergency_live | Dump lean/graph-check-emergency.sh EmergencyLeaseHasARosterQuorum EmergencyLeaseIsOneRound NoAgentHoldsAnEmergencySeat CallsAreAllowlisted ThinkerStillCoupled ActivationIsForensic EmergencyNeverCoupled EmergencyCallsWithoutObserver | Mut = "none"; MaxRound = 2 | NextL |
ROWS
}

# Script(s) | the modules whose lines cover them (a Dump row's module is <Module>Dump)
scripts() {
cat <<'SCRIPTS'
RulesFloorNV-run.sh | RulesFloorNV
RulesFloorNV_rev5-run.sh | RulesFloorNV_rev5
NonComposition-run.sh | NonComposition
bootstrap-run.sh | Anchor BreakGlass
lease-run.sh | Lease
Lease_A1-run.sh | Lease_A1
floor-run.sh | FloorComposition FloorRouting
confinement-run.sh, confinement-gen-results.sh | Confinement Confinement_A1
seats-run.sh | Seats
observers-run.sh | Observers
coupling-run.sh | Coupling
runcoupling-run.sh | RunCoupling
runseats-run.sh | RunSeats
runconfinement-run.sh, runconfinement-gen-results.sh | RunConfinement
emergency-run.sh, emergency-gen-results.sh | Emergency
a1-run.sh | BreakGlass_A1 NonComposition_A1
toollist-run.sh, toollist-gen-results.sh | ToolList
operators-run.sh, operators-gen-results.sh | Operators
correlator-run.sh, correlator-gen-results.sh | Correlator
labels-run.sh, labels-gen-results.sh | Labels
live-gen-results.sh | Coupling_live Emergency_live
lean/graph-check.sh | SeatsDump FloorCompositionDump
lean/graph-check-emergency.sh | EmergencyDump Emergency_liveDump
SCRIPTS
}
# The two that are not model-checking runs of a transition system; their reasons are printed after the lines.
others="mechanism-trace-run.sh simulate-run.sh"

trim() { local s=$1; s=${s#"${s%%[![:space:]]*}"}; s=${s%"${s##*[![:space:]]}"}; printf '%s' "$s"; }
d16() { shasum -a 256 "$1" | cut -c1-16; }
# Every local module a module reaches through EXTENDS, in dependency order.
chain() {
  local m=$1 d
  case " $seen " in *" $m "*) return ;; esac
  for d in $(grep -m1 '^EXTENDS' "$m.tla" | sed 's/^EXTENDS//; s/,/ /g'); do
    [ -f "$d.tla" ] && chain "$d"
  done
  seen="$seen $m"
}
# The distinct-state count of TLC's last statistics line, if it printed one.
distinct() { grep -E '^[0-9]+ states generated, [0-9]+ distinct states found' "$1" | tail -1 | sed -E 's/^.*, ([0-9]+) distinct states found.*$/\1/'; }
# The last state of TLC's error trace, on one line.
laststate() {
  awk '/^State [0-9]+: / || /is violated by the initial state:$/ { s = ""; on = 1; next }
       on && (/^[0-9]+ states generated/ || /^The depth/ || /^Finished/ || /^Progress/ || /^Error/) { on = 0 }
       on { s = s " " $0 }
       END { print s }' "$1" \
    | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//; s/^\/\\ //; s/\{ /{/g; s/ \}/}/g; s/\[ /[/g; s/ \]/]/g; s/<< /<</g; s/ >>/>>/g'
}
# One TLC run: tlc <dir> <wrapper> <spec> <invariant or empty> <tag> <workers>; output in <dir>/<tag>.out, exit code returned.
tlc() {
  local d=$1 w=$2 spec=$3 inv=$4 tag=$5 wk=$6
  { echo "SPECIFICATION $spec"; [ -n "$inv" ] && echo "INVARIANT $inv"; echo "CONSTANTS"; printf '%s\n' "$cfgc"; } > "$d/$tag.cfg"
  mkdir -p "$d/$tag.jtmp"
  (cd "$d" && java -XX:+UseParallelGC -Djava.io.tmpdir="$d/$tag.jtmp" -cp "$jar" tlc2.TLC -config "$tag.cfg" \
      -workers "$wk" -fp 0 -deadlock -metadir "$d/$tag.meta" "$w.tla") > "$d/$tag.out" 2>&1
}
# HOLDS, VIOLATED (the invariant named) or ERROR.
verdict() { # <out> <exit code> <invariant>
  if [ "$2" -eq 0 ] && grep -q "^Model checking completed. No error has been found." "$1"; then echo HOLDS
  elif [ "$2" -eq 12 ] && grep -q "^Error: Invariant $3 is violated" "$1"; then echo VIOLATED
  else echo ERROR; fi
}
tlcerror() { grep -m1 -E '^Error|Exception|rror:' "$1" | cut -c1-200; }
# A script's name, its digest, and a note if it no longer passes -deadlock.
named() {
  if [ ! -f "$1" ]; then printf '%s (not found)' "$1"
  elif grep -q -e '-deadlock' "$1"; then printf '%s (sha256 %s)' "$1" "$(d16 "$1")"
  else printf '%s (sha256 %s, which no longer passes -deadlock)' "$1" "$(d16 "$1")"; fi
}

only=${ONLY:-}
selected() { [ -z "$only" ] || printf '%s\n' "$1" | grep -qE "$only"; }

seen=""
while IFS='|' read -r mod rest; do
  mod=$(trim "$mod"); case "$mod" in ''|\#*) continue ;; esac
  selected "$mod" && chain "$mod"
done < <(rows)
mods=""
for m in $seen; do mods="$mods${mods:+ · }$m.tla (sha256 $(d16 "$m.tla"))"; done
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)

echo "TOPAK — the -deadlock audit: where the modules the run scripts check have states with no successor, at the constants their results files use, unmutated"
echo "Runner: deadlock-audit.sh (sha256 $(d16 deadlock-audit.sh)) · TLC $tlcv (jar sha256 $(d16 "$jar")) · $(java -version 2>&1 | head -1) · TLC -workers $workers -fp 0 -deadlock${only:+ · rows: only modules matching $only}"
echo "Modules: $mods"
echo "Every run script listed below passes -deadlock, which turns off TLC's report of a state with no successor, a terminal state. Each line is one module at one set of constants, unmutated, through a wrapper that EXTENDS it and adds only definitions, so the state graph is the module's own. TLC checks INVARIANT NotTerminal (Terminal == ~ENABLED of the specification's next-state relation) and, where that is violated, INVARIANT TerminalAtBound (Terminal => AtBound, the bound being the module's own end, as the line names it). A line claims that at its constants every terminal state is at that bound, or there is none, so that the flag turns off the report of the module's end and hides nothing else. It claims nothing at other constants, where an end can fall elsewhere, or under a mutation, whose rows may stop anywhere and need only reach their counterexample. Nor does it claim that the module never stalls: a state whose only step leaves it unchanged has a successor, for ENABLED as for TLC's check, so neither sees it."
echo

tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-deadlock.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
trap 'exit 2' INT TERM HUP
: > "$tmp/lines"
n=0; nnone=0; nbound=0; nstray=0; nerr=0
while IFS='|' read -r mod inst consts next atb; do
  mod=$(trim "$mod"); case "$mod" in ''|\#*) continue ;; esac
  selected "$mod" || continue
  inst=$(trim "$inst"); consts=$(trim "$consts"); next=$(trim "$next"); atb=$(trim "$atb")
  n=$((n + 1)); d="$tmp/$n"; mkdir -p "$d"
  cfgc=$(printf '%s\n' "$consts" | tr ';' '\n' | sed 's/^ *//; s/ *$//; /^$/d; s/^/  /')
  shown=$(printf '%s\n' "$consts" | sed 's/ *; */ · /g')
  seen=""; chain "$mod"
  for m in $seen; do cp "$m.tla" "$d/"; done
  case "$inst" in
    "EXTENDS "*)
      spec=${inst#EXTENDS }; base=$mod; key=$mod
      label=$mod; [ "$spec" = Spec ] || label="$mod ($spec)"
      grep -qE "^$spec *== *Init /\\\\ \\[\\]\\[$next\\]_vars" "$mod.tla" || {
        echo "$label | $shown | ERROR: $mod.tla has no $spec == Init /\\ [][$next]_vars"; echo "$key	error" >> "$tmp/lines"
        nerr=$((nerr + 1)); continue; } ;;
    "Dump "*)
      rest=${inst#Dump }; script=${rest%% *}; props=${rest#* }; base=${mod}Dump; key=$base; spec=DSpec
      label="$base ($script's construction)"
      grep -qE "^[A-Za-z0-9_]+ *== *Init /\\\\ \\[\\]\\[$next\\]_vars" "$mod.tla" || {
        echo "$label | $shown | ERROR: $mod.tla has no specification Init /\\ [][$next]_vars"; echo "$key	error" >> "$tmp/lines"
        nerr=$((nerr + 1)); continue; }
      fields=$(for p in $props; do printf '%s |-> %s, ' "$p" "$p"; done | sed 's/, $//')
      printf '%s\n' "---- MODULE $base ----" "EXTENDS $mod" "VARIABLE props" "Props == [$fields]" \
        "DInit == Init /\\ props = Props" "DNext == $next /\\ props' = Props'" \
        "DSpec == DInit /\\ [][DNext]_<<vars, props>>" "====" > "$d/$base.tla"
      next=DNext ;;
    *)
      echo "$mod | $shown | ERROR: unknown instance \"$inst\""; echo "$mod	error" >> "$tmp/lines"
      nerr=$((nerr + 1)); continue ;;
  esac
  w=${base}_DL
  printf '%s\n' "---- MODULE $w ----" \
    "(* Written by deadlock-audit.sh. Adds only definitions to $base; the state graph is $base's own. *)" \
    "EXTENDS $base" \
    "Terminal        == ~ENABLED $next" \
    "NotTerminal     == ~Terminal" \
    "AtBound         == ${atb:-FALSE}" \
    "TerminalAtBound == Terminal => AtBound" \
    "====" > "$d/$w.tla"
  tlc "$d" "$w" "$spec" NotTerminal nt "$workers"; v=$(verdict "$d/nt.out" $? NotTerminal)
  case "$v" in
    HOLDS)
      echo "$label | $shown | $(distinct "$d/nt.out") distinct states | no terminal state"
      echo "$key	none" >> "$tmp/lines"; nnone=$((nnone + 1)) ;;
    VIOLATED)
      tlc "$d" "$w" "$spec" TerminalAtBound tb "$workers"; v=$(verdict "$d/tb.out" $? TerminalAtBound)
      case "$v" in
        HOLDS)
          echo "$label | $shown | $(distinct "$d/tb.out") distinct states | every terminal state at the bound: $atb"
          echo "$key	bound" >> "$tmp/lines"; nbound=$((nbound + 1)) ;;
        VIOLATED)
          tlc "$d" "$w" "$spec" TerminalAtBound tb1 1; first=$(laststate "$d/tb1.out")
          [ -n "$first" ] || first="the state could not be read from the output of TLC"
          tlc "$d" "$w" "$spec" "" all "$workers"; v=$(verdict "$d/all.out" $? none)
          [ "$v" = HOLDS ] && states=$(distinct "$d/all.out") || states="no count of"
          echo "$label | $shown | $states distinct states | STRAY DEADLOCK: $first"
          echo "$key	stray" >> "$tmp/lines"; nstray=$((nstray + 1)) ;;
        *)
          echo "$label | $shown | ERROR on TerminalAtBound: $(tlcerror "$d/tb.out")"
          echo "$key	error" >> "$tmp/lines"; nerr=$((nerr + 1)) ;;
      esac ;;
    *)
      echo "$label | $shown | ERROR on NotTerminal: $(tlcerror "$d/nt.out")"
      echo "$key	error" >> "$tmp/lines"; nerr=$((nerr + 1)) ;;
  esac
  rm -rf "$d"
done < <(rows)
if selected Operators; then
  echo
  echo "Not run: Operators at Ops = {\"a\", \"b\", \"c\"} (rows w9 and nsv3 of Operators-results-2026.10.04.txt). Its graph has more than 91,597,194 distinct states: a run on 2026.10.06 had found that many, with 36,836,627 still queued, when it was stopped at 40 minutes, with no terminal state among them. For any Ops each operator has exactly one of Vouch(o) and Unvouch(o) enabled, so no state is terminal; that is a reading of Operators.tla, not a check."
fi
echo
echo "The scripts that pass -deadlock to model-check a transition system, with the lines above that cover each:"
while IFS='|' read -r scr ms; do
  scr=$(trim "$scr"); [ -z "$scr" ] && continue
  out=""; tn=0; tb=0; ts=0; te=0
  for m in $(trim "$ms"); do
    nn=$(awk -F'\t' -v m="$m" '$1 == m && $2 == "none"' "$tmp/lines" | wc -l | tr -d ' ')
    nb=$(awk -F'\t' -v m="$m" '$1 == m && $2 == "bound"' "$tmp/lines" | wc -l | tr -d ' ')
    ns=$(awk -F'\t' -v m="$m" '$1 == m && $2 == "stray"' "$tmp/lines" | wc -l | tr -d ' ')
    ne=$(awk -F'\t' -v m="$m" '$1 == m && $2 == "error"' "$tmp/lines" | wc -l | tr -d ' ')
    t=$((nn + nb + ns + ne)); [ $t -eq 0 ] && continue
    tn=$((tn + nn)); tb=$((tb + nb)); ts=$((ts + ns)); te=$((te + ne))
    parts=""
    [ $nb -gt 0 ] && parts="$parts, $nb with every terminal state at the bound"
    [ $nn -gt 0 ] && parts="$parts, $nn with no terminal state"
    [ $ns -gt 0 ] && parts="$parts, $ns with a STRAY DEADLOCK"
    [ $ne -gt 0 ] && parts="$parts, $ne ERROR"
    [ $t -eq 1 ] && lines="1 line" || lines="$t lines"
    out="$out${out:+; }$m ($lines: ${parts#, })"
  done
  [ -z "$out" ] && continue
  if [ $ts -gt 0 ]; then c="a stray deadlock, on its line above"
  elif [ $te -gt 0 ]; then c="not settled, since a line is ERROR"
  elif [ $tb -gt 0 ] && [ $tn -gt 0 ]; then c="where there are terminal states, every one is at the bound its line names, and the flag turns off the report of that end and hides nothing else; elsewhere the flag is inert"
  elif [ $tb -gt 0 ]; then c="every terminal state is at the bound its line names, and the flag turns off the report of that end and hides nothing else"
  else c="no terminal state at these constants; the flag is inert there"; fi
  names=""
  for f in $(printf '%s' "$scr" | tr ',' ' '); do names="$names${names:+, }$(named "$f")"; done
  echo "  $names: $out. So: $c."
done < <(scripts)
echo "  premise-corrections-results.sh passes no flag itself. It runs coupling-run.sh and runcoupling-run.sh unmutated, at constants on the lines above, and floor-run.sh under mutations, which this audit does not cover."
echo
echo "The scripts that pass -deadlock but are not model-checking runs of a transition system, with their reason:"
if grep -qE '^TraceNext *== *TraceStep \\/ Done' Mechanism.tla && grep -qE '^Done *== *i = Len\(Trace\) /\\ UNCHANGED vars' Mechanism.tla; then
  echo "  $(named mechanism-trace-run.sh), and mechanism-trace-results.sh (sha256 $(d16 mechanism-trace-results.sh)), which runs it: a replay of one recorded trace through Mechanism.tla (sha256 $(d16 Mechanism.tla)) by TraceSpec, whose next-state relation is TraceNext == TraceStep \\/ Done. TraceStep is enabled at every step before the trace's end, and Done == i = Len(Trace) /\\ UNCHANGED vars is a step at the end that leaves the state unchanged, which TLC counts as a successor. So a replay has no terminal state and the flag is inert: the replay ends at the trace's end by design, but by stuttering there, and Done is what keeps TLC from reporting that end as a deadlock."
else
  echo "  mechanism-trace-run.sh: NOT CHECKED. Mechanism.tla (sha256 $(d16 Mechanism.tla)) no longer has TraceNext == TraceStep \\/ Done with Done == i = Len(Trace) /\\ UNCHANGED vars, which the reason given here rests on."
fi
if grep -q -- '-simulate' simulate-run.sh; then
  echo "  $(named simulate-run.sh): TLC's simulation mode, which draws behaviours at random, each to -depth. Where a behaviour reaches a terminal state the flag ends it there and the next is drawn; without the flag the first terminal state any behaviour reaches stops the run with \"Deadlock reached\", so in a module that ends at its bounds the first behaviour to end would stop the run. The flag is needed for that. It runs at constants exhaustive checking cannot reach, which no line above covers, so where its behaviours end is not checked, and a NO ERROR SAMPLED line says nothing about it."
fi
listed=" $(scripts | cut -d'|' -f1 | tr ',' ' ' | tr '\n' ' ') $others "
unlisted=""
for f in $( (grep -l -e '-deadlock' *.sh; cd lean && grep -l -e '-deadlock' *.sh | sed 's|^|lean/|'; cd ../../tools && grep -l -e '-deadlock' *.sh | sed 's|^|../tools/|') 2>/dev/null); do
  [ "$f" = deadlock-audit.sh ] && continue
  case "$listed" in *" $f "*) ;; *) unlisted="$unlisted $f" ;; esac
done
echo
if [ -n "$unlisted" ]; then echo "Scripts in spec/, spec/lean/ and tools/ that pass -deadlock and are not listed here:$unlisted"
else echo "Every script in spec/, spec/lean/ and tools/ that passes -deadlock is listed here."; fi
echo
echo "Lines: $n · no terminal state: $nnone · every terminal state at the bound: $nbound · STRAY DEADLOCK: $nstray · ERROR: $nerr"
[ $nstray -gt 0 ] && exit 1
[ $nerr -gt 0 ] && exit 2
exit 0
