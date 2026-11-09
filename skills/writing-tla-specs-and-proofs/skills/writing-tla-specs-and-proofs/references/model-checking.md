# Model checking: runs, rows, results files

TLC's job in this method is existential and bounded: at small constants,
every mutation reaches a bad state, every witness is reachable, every fair
spec has a behaviour, and no property is violated under the unmutated
mechanism. Its result is **non-vacuity and discrimination**. The word for it
is **checked**; the word **proved** is reserved for the prover.

## Contents

- [The run script](#the-run-script)
- [The row matrix](#the-row-matrix)
- [The results file](#the-results-file)
- [Row lists and generators](#row-lists-and-generators)
- [The deadlock flag](#the-deadlock-flag)
- [Practical constants and simulation](#practical-constants-and-simulation)
- [Liveness rows](#liveness-rows)
- [Reading a counterexample](#reading-a-counterexample)

## The run script

One per module, next to it. It writes the `.cfg` itself, so no `.cfg` is
tracked, and prints one row per run:

```sh
#!/bin/bash
# usage: coupling-run.sh name mut invariant [K] [R] [MaxRound]
name=$1; mut=$2; inv=$3; k=${4:-1}; r=${5:-3}; mr=${6:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  K = $k
  R = $r
  MaxRound = $mr
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock \
        -metadir /tmp/tlc_$name Coupling.tla 2>&1)
if echo "$out" | grep -q "is violated"; then res="COUNTEREXAMPLE"
elif echo "$out" | grep -q "No error has been found"; then res="HOLDS"
else res="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | Mut=$mut | $inv | $res | $states"
[ "$res" = "ERROR" ] && echo "$out" | tail -25
rm -f $name.cfg
```

Points that matter:

- **Three verdicts, and `ERROR` is loud.** A parse error, a missing
  constant or a Java exception must not read as `HOLDS`. Print the tail of
  TLC's output on `ERROR`.
- **The checker is a tracked jar with a wrapper**, found at a fixed relative
  path or `$TLA_JAR`, so the digest printed in results files names one
  build.
- **`-metadir` per run** in a temp location so parallel runs do not
  collide, and so that nothing is written beside the module.
- **The state count** is part of the row. It is the cheapest check that a
  mutation changed the model as intended (a removed guard grows the graph)
  and that a liveness module's `NextL` is the base `Next` (same count).
- **Defaults are the small constants**; a row that needs another value
  passes it.

## The row matrix

For a module with properties P1..Pn, mutations M1..Mk and witnesses W1..Wm,
the results file carries:

| Rows | Mut | Property | Expected |
|------|-----|----------|----------|
| one per property | `none` | Pi | `HOLDS` |
| one per (mutation, property it must break) | Mj | Pi | `COUNTEREXAMPLE` |
| one per (mutation, property it must **not** break) | Mj | Pi | `HOLDS` |
| one per witness | `none` | Wl | `COUNTEREXAMPLE` |
| `Safe`, the conjunction | `none` | Safe | `HOLDS` |

The third kind of row is the one most often skipped and the one the proofs
later need: it is the "Breaks under" column, and a theorem's hypothesis is
exactly the set of mutations whose rows against that property read
`COUNTEREXAMPLE`. When a proof's hypothesis and the results file disagree,
run the missing row; the proof has usually found a row that was never run
(a mutation that breaks a second property) or a transcription error.

Name rows by a short module prefix, the mutation and the property:
`c-none-unread`, `c-mark-unread`, `w-refused`.

## The results file

```
TOPAK — Coupling.tla (ADR-0039 §8), TLC results 2026.09.29
jar: tla2tools.jar v1.7.4 · constants: K=1, R=3, MaxRound=2; one Thinker, its cell Observer, one correlator
expected: none HOLDS on all three; M_NOCOUPLE breaks §2 (and UnreadBounded); M_MARK and M_ROUNDS break UnreadBounded only; M_CORR breaks §4 only; witnesses VIOLATED
c-none-noadmit | Mut=none | NoAdmitWithoutLiveObserver | HOLDS | 1124 distinct states found
c-none-unread | Mut=none | UnreadBounded | HOLDS | 1124 distinct states found
c-nocouple-noadmit | Mut=M_NOCOUPLE | NoAdmitWithoutLiveObserver | COUNTEREXAMPLE | 12 distinct states found
c-mark-unread | Mut=M_MARK | UnreadBounded | COUNTEREXAMPLE | 84 distinct states found
c-mark-noadmit | Mut=M_MARK | NoAdmitWithoutLiveObserver | HOLDS | 1604 distinct states found
w-refused | Mut=none | NeverRefused | COUNTEREXAMPLE | 12 distinct states found
```

Rules:

- **Dated name**, `<Module>-results-<date>.txt`, and a new file for every
  rerun that changes anything. A file never changes once written.
- **Header**: the module and the design record it serves; the checker's
  version and digest and the module's digest; the constants; an
  **expected** line stating in prose what every row should read. The
  generator compares each row to its expectation and exits non-zero on a
  mismatch, so the file cannot be green by accident.
- **Never hand-edited.** Regenerate from the row list. If a row list does
  not exist yet, write one before the second run of the module.
- **Cited by digest** from the design record that relies on it; from then
  on the module it names is frozen (see [evidence.md](evidence.md)).

## Row lists and generators

Once a module has more than a handful of rows, move them to a row list and
regenerate the results file from it:

```
# Rows for live-gen-results.sh Coupling_live: name mut spec kind property expected [CONST=value ...] [states=N]
s-none-safe        none      SpecL    INVARIANT  Safe             HOLDS     states=1124
d-none-deadlock    none      SpecL    DEADLOCK   Safe             HOLDS     states=1124
w-none-refused     none      SpecL    INVARIANT  NeverRefused     VIOLATED
l-a12-admitstall   none      SpecA12  PROPERTY   AdmitStallEnds   HOLDS
l-nokeepup-admit   none      SpecNoKeepUp PROPERTY AdmitStallEnds VIOLATED
l-a12-k2           none      SpecA12  PROPERTY   AdmitStallEnds   HOLDS     K=2 R=4 MaxRound=3
```

The generator writes the header (title, module digest, checker digest,
constants, the expected line taken from a `# expected:` comment in the row
list), runs one TLC section per row, prints each section's verdict and
whether it is the expected one, and exits non-zero if any row is `ERROR`,
not as expected, or if the row list has no rows. **A generator that
processes zero rows must fail**, or an empty list is a green file.

`kind` distinguishes `INVARIANT`, `PROPERTY` (TLC's liveness checker) and
`DEADLOCK` (the invariant with the deadlock check on, where the verdict is
"deadlock reached" or not). `states=N` asserts the exact distinct-state
count, which is how a liveness module shows its `NextL` is the base `Next`
under a base mutation.

## The deadlock flag

Pass `-deadlock` by default: most modules have an action that is always
enabled (an observer's lease toggles; a correlator beats), so TLC's
deadlock report would fire only at the module's own bound (`round =
MaxRound`, every seat granted) and would be noise. But the flag hides
real terminal states, so **audit it separately**: for each module and the
constants its results use, unmutated, a wrapper module that `EXTENDS` the
base and adds `Terminal == ~ENABLED Next`, `AtBound == <the bound the row
states>`, and `TerminalAtBound == Terminal => AtBound`; TLC with
`INVARIANT NotTerminal`, and where that is violated, `INVARIANT
TerminalAtBound`. Every terminal state must be at a bound the module
imposes. The audit is a dated results file like any other.

A stall in a module with always-enabled actions is a **livelock**, which
no deadlock check sees. If the design claims the stall ends, that is a
leads-to property (below).

## Practical constants and simulation

Three distinct kinds of run, three distinct words:

| Run | Constants | Result | Word |
|-----|-----------|--------|------|
| Exhaustive, small | the smallest that make every mutation and witness discriminable (two principals, `K = 1`, two rounds) | `HOLDS` / `COUNTEREXAMPLE` | **checked** |
| Exhaustive, practical | the values the design names as placeholders (`K = 8`, `R = 64`, three rounds), into a file suffixed `-medium`; a row that does not finish is recorded as such with the time allowed | the same | **checked at those constants** |
| `-simulate` | larger still, random behaviours to a depth | `NO ERROR SAMPLED` / `COUNTEREXAMPLE` | **sampled**, never cited as a check |

A simulation script prints `simulate depth=D traces=N seed=S` in its row
and `NO ERROR SAMPLED` rather than `HOLDS`, so the file cannot be misread.
TLC in simulation mode prints no "No error has been found"; a run that
finishes without an `Error` line sampled its traces and found nothing.

## Liveness rows

A liveness module extends the safety module (see
[spec-design.md](spec-design.md)) and its row list has five kinds of row:

1. **Safety carried over**: `Safe` under `SpecL` for `none` and each
   liveness mutation, with `states=N` equal to the base module's count
   where `NextL` is the base `Next`.
2. **Deadlock, on**: `DEADLOCK` rows showing no state is terminal, so a
   stall is a livelock and TLC's deadlock check is not the check.
3. **Witnesses**, under `none` and under the mutation that reaches every
   base state, to show that mutation is invisible to safety.
4. **Each leads-to property under the spec it needs**, `HOLDS`, at two sets
   of constants; and **under each spec that drops or weakens one
   condition**, `VIOLATED`. One row per condition, so the file shows each
   condition is load-bearing and each weaker form proposed (weak where
   strong is needed; fairness on any heartbeat instead of the one that
   keeps up) fails.
5. **`NoBehaviour` under every fair spec a `HOLDS` row uses**, `VIOLATED`,
   so the fair spec has a behaviour.

Run liveness rows with **one worker and a fixed fingerprint function**
(`-workers 1 -fp 0`): with TLC's random choice a liveness counterexample
changes from run to run, and the results file would not be reproducible.
Give each row its own `java.io.tmpdir` as well as `-metadir`: TLC unpacks
the standard modules into the shared temp directory, and a concurrent run
can remove them underneath this one.

TLC reads a state with no successor as stuttering forever, which is how
TLA+ reads a behaviour that stops; a leads-to that holds only because the
model never stalls is what the `DEADLOCK` rows rule out.

## Reading a counterexample

A `COUNTEREXAMPLE` row where `HOLDS` was expected is one of three things,
in order of likelihood:

1. **A property stated too strongly** for the model: `PriorUnread` written
   for `MaxRound = 2` and run at 3; a witness's flag read by a property.
   Fix the statement, and say in the header what it assumes.
2. **A missing guard in the specification**: the design text needs the
   check and the module does not have it. This is a finding; record it
   against the design document, add the guard, and consider making the old
   text a mutation.
3. **A design error.** The rarest and the most valuable. The row is the
   evidence; keep it in a dated file even after the design changes.

A `HOLDS` row where `COUNTEREXAMPLE` was expected means the mutation does
not do what its header says, or the property does not depend on that
guard. Either way the header is wrong; the proof's weakest-hypothesis rule
will meet the same fact from the other side.
