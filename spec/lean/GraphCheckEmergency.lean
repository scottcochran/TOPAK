import GraphCheckCore
import TopakSpec.Mirror.Emergency
/-!
# Checking the Emergency encoding against TLC's state graphs

`graph-check-emergency.sh` has TLC dump every reachable state and transition of `Emergency.tla` under its eight values
of `Mut`, and of `Emergency_live.tla` under `none` and its own two, at `MaxRound = 2`, with a derived variable `props`
carrying each property's value, and `dot2lines.py` turns each dump into lines. This program decodes them and evaluates
the encoding, `TopakSpec/Emergency.lean`, on them through its proved mirror (`TopakSpec/Mirror/Emergency.lean`), with
`GraphCheckCore.lean`'s `check`: every TLC edge is a step of the encoding's relation, every step of that relation from
a TLC state is a TLC edge or a stutter, the TLC initial states are exactly the encoding's `Init` (through `init_iff`),
and each property has, in every TLC state, the value TLC gave it.

`Emergency`'s relation is `Next` (through `next_iff`: the target is among `succC`). `Emergency_live`'s graph is its
`SpecL`'s, and its relation is `NextL` (through `nextL_iff`: the target is among `succLC`). Its two properties over
`ENABLED` ride in `props` like its other six: TLC evaluates them in each state, and they are compared as the others
are. The mirror fixes `MaxRound = 2`, the value the TLC
results use: the encoding's theorems are for every `MaxRound`, and this check covers `MaxRound = 2` only.

This is a program of its own, with its own script and results series (`GraphCheckEmergency-results-*.txt`). The
premise binding (`spec/theorem-premise-binding.json`) takes the faithfulness of the `Seats` and `FloorComposition`
encodings from the newest `GraphCheck-results-*.txt`, and only while every file that file names is as the tree has
it; kept out of that file, `Emergency`'s files can change without touching those two premises. The two series
share `Prelude.lean`, `GraphCheckCore.lean`, `dot2lines.py`, `lakefile.toml` and `lean-toolchain`, and an
edit to any of them stales both.

usage: `graphcheck-emergency <module> <mut> <graph.lines>`, the module `Emergency` or `Emergency_live`
-/

open Lean

/-! ## Emergency and Emergency_live, at `MaxRound = 2` -/

namespace EmergencyG
open Topak.Spec.Emergency Topak.Spec.Emergency.Mirror

def field (j : Json) (k : String) : Except String Json := j.getObjVal? k
def str (j : Json) (k : String) : Except String String := do (← field j k).getStr?
def bool (j : Json) (k : String) : Except String Bool := do (← field j k).getBool?
def nat (j : Json) (k : String) : Except String Nat := do (← field j k).getNat?
def elems (j : Json) : Except String (Array Json) := do (← field j "$s").getArr?

def tool? : String → Except String Tool
  | "t1" => pure .t1 | "t2" => pure .t2 | "te" => pure .te | "tx" => pure .tx | s => throw s!"tool {s}"
def member? : String → Except String Member
  | "r1" => pure .r1 | "r2" => pure .r2 | "r3" => pure .r3 | s => throw s!"member {s}"
def holder? : String → Except String Holder
  | "h" => pure .h | "g" => pure .g | "none" => pure .none | s => throw s!"holder {s}"
def grantor? : String → Except String Grantor
  | "none" => pure .none | "roster" => pure .roster | "operator" => pure .operator | s => throw s!"by {s}"
def seat? : String → Except String Seat
  | "emergency" => pure .emergency | "thinker" => pure .thinker | s => throw s!"seat {s}"

def tools? (j : Json) : Except String (Tool → Bool) := do
  let ts ← (← elems j).mapM fun x => do tool? (← x.getStr?)
  pure fun t => ts.contains t
def members? (j : Json) : Except String (Member → Bool) := do
  let rs ← (← elems j).mapM fun x => do member? (← x.getStr?)
  pure fun r => rs.contains r

def em? (j : Json) : Except String CEm := do
  pure ⟨← bool j "live", ← nat j "round", ← holder? (← str j "holder"), ← tools? (← field j "envelope"),
    ← bool j "quorate", ← grantor? (← str j "by"), ← bool j "renewed"⟩

def call? (j : Json) : Except String CallKey := do
  pure ⟨← seat? (← str j "seat"), ← tool? (← str j "tool"), ← bool j "allowlisted", ← bool j "observed"⟩

/-- An activation record. The mirror's are of rounds 1 and 2, the only ones `Activate` writes at `MaxRound = 2`. -/
def rec? (j : Json) : Except String RecKey := do
  let second ← match ← nat j "round" with
    | 1 => pure false
    | 2 => pure true
    | n => throw s!"record round {n}: the mirror has rounds 1 and 2 (MaxRound = 2)"
  let a ← members? (← field j "approvers")
  pure ⟨second, ← holder? (← str j "holder"), a .r1, a .r2, a .r3⟩

def decode (j : Json) : Except String CState := do
  let calls ← (← elems (← field j "calls")).mapM call?
  let recs ← (← elems (← field j "records")).mapM rec?
  pure ⟨← tools? (← field j "domainTools"), ← members? (← field j "approvals"), ← em? (← field j "em"),
    ← tools? (← field j "thinkerAllow"), ← bool j "obsLive", fun k => calls.contains k, ← bool j "refused",
    fun k => recs.contains k⟩

instance : Inhabited CState := ⟨cInit⟩

def mut? : String → Except String Mut
  | "none" => pure .none | "M_NOQUORUM" => pure .M_NOQUORUM | "M_REGRANT" => pure .M_REGRANT
  | "M_RENEW" => pure .M_RENEW | "M_AGENT" => pure .M_AGENT | "M_X1" => pure .M_X1
  | "M_UNCOUPLE" => pure .M_UNCOUPLE | "M_ERASE" => pure .M_ERASE | "M_EMCOUPLE" => pure .M_EMCOUPLE
  | "M_EMCOUPLE2" => pure .M_EMCOUPLE2 | s => throw s!"Mut {s}"

/-- Emergency.tla's six properties. -/
def safeProps : List (String × (CState → Bool)) :=
  [("EmergencyLeaseHasARosterQuorum", elhqB), ("EmergencyLeaseIsOneRound", eloB),
   ("NoAgentHoldsAnEmergencySeat", nahB), ("CallsAreAllowlisted", caaB), ("ThinkerStillCoupled", tscB),
   ("ActivationIsForensic", aifB)]

/-- Emergency.tla's `Spec`. -/
def mirror (m : Mut) : Mirror CState := { decode, succ := succC m, eq := eqC, cInit, props := safeProps }

/-- Emergency_live.tla's `SpecL`, with its two properties over `ENABLED`. -/
def mirrorL (m : Mut) : Mirror CState :=
  { decode, succ := succLC m, eq := eqC, cInit, rel := "NextL",
    props := safeProps ++ [("EmergencyNeverCoupled", encB m), ("EmergencyCallsWithoutObserver", ecwoB m)] }

end EmergencyG

def main (args : List String) : IO UInt32 := do
  match args with
  | ["Emergency", m, path] =>
    let mm ← IO.ofExcept (EmergencyG.mut? m)
    pure (if ← check s!"Emergency Mut={m}" (EmergencyG.mirror mm) path then 0 else 1)
  | ["Emergency_live", m, path] =>
    let mm ← IO.ofExcept (EmergencyG.mut? m)
    pure (if ← check s!"Emergency_live Mut={m}" (EmergencyG.mirrorL mm) path then 0 else 1)
  | _ =>
    IO.println "usage: graphcheck-emergency <module> <mut> <graph.lines>"
    pure 2
